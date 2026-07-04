import asyncio
from datetime import datetime
from typing import Optional,Tuple,List,Dict
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..models import Candidate,Score,User,CandidateStatus
from app.services.broadcaster import score_broadcaster
from google import genai
from logging import Logger
from google.genai import errors

class CandidateService:
    def __init__(self,db:Session,gemini_client: genai.Client):
        self.db=db
        self.gemini_client = gemini_client

    def list_candidates(
            self,
            status:Optional[str]=None,
            role_applied:Optional[str]=None,
            skill:Optional[str]=None,
            keyword:Optional[str]=None,
            page:int=1,
            page_size:int=20
            )->Tuple[list[Candidate],int]:
        
        query=self.db.query(Candidate).filter(Candidate.deleted_at.is_(None))

        if status:
            query=query.filter(Candidate.status==status)
        if role_applied:
            query=query.filter(Candidate.role_applied==role_applied)
        if skill:
            query=query.filter(Candidate.skills.contains(skill))
        if keyword:
            like=f"%{keyword}%"
            query=query.filter(or_(Candidate.name.alike(like),Candidate.email.alike(like)))
        
        total=query.count()

        page=max(page,1)
        page_size=min(max(page_size,1),50)
        offset=(page-1)*page_size
        items=(
            query.order_by(Candidate.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items,total
    
    def get_scores_for_viewer(self, candidate_id: int, viewer: User) -> List[Score]:
        """Reviewers only see their own scores; admins see everyone's."""
        query = self.db.query(Score).filter(Score.candidate_id == candidate_id)
        if viewer.role != "admin":
            query = query.filter(Score.reviewer_id == viewer.id)
        return query.order_by(Score.created_at.desc()).all()
 
    def redact_for_viewer(self, candidate: Candidate, viewer: User) -> Candidate:
        """internal_notes is admin-only. Strip it server-side rather than
        trusting the frontend to hide it - the frontend is not a security
        boundary."""
        if viewer.role != "admin":
            candidate.internal_notes = None
        return candidate
    
    def get_candidate(self,candidate_id:int)->Optional[Candidate]:
        return (
            self.db.query(Candidate)
            .filter(Candidate.id==candidate_id,Candidate.deleted_at.is_(None))
            .first()
        )

    async def add_score(self,candidate_id:int,reviewer:User,category:str,score:int,note:Optional[str])->Score:
        candidate=self.get_candidate(candidate_id)
        if candidate is None:
            raise ValueError("Candidate not found")
        record =Score(
           candidate_id=candidate_id,
           category=category,
           rating=score,
           reviewer_id=reviewer.id,
           note=note,
        )

        self.db.add(record)
        if candidate.status==CandidateStatus.new:
           candidate.status=CandidateStatus.reviewed
        self.db.commit()
        self.db.refresh(record)

        
        await score_broadcaster.broadcast_score_update(
            candidate_id=candidate_id,
            category=category,
            score=score,
            reviewer_name=reviewer.email
        )
    
        
        return record

    async def generate_summary(self,candidate_id:str)->Dict[str, str]:
        candidate=self.get_candidate(candidate_id)
        if candidate is None:
            raise ValueError("Candidate Not Found")
        # await asyncio.sleep(2)
        skills_str=", ".join(candidate.skills) if candidate.skills else "no listed skills"
        prompt = (
            f"Write a concise executive summary for this job applicant.\n"
            f"Name: {candidate.name}\n"
            f"Role Applied For: {candidate.role_applied}\n"
            f"Skills: {skills_str}\n"
            f"Status: {candidate.status}"
        )
        try:
            # response = await self.gemini_client.aio.models.generate_content(
            #     model="gemini-2.5-flash",
            #     contents=prompt
            # )
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
            )
            summary = response.text.strip()
            summary_method = "llm"

        except Exception as e:
            logger.error(f"Gemini summary generation failed for candidate {candidate_id}: {e}", exc_info=True)
            summary = self._fallback_summary(candidate, skills_str)
            summary_method = "fallback"

        candidate.ai_summary = summary
        await asyncio.to_thread(self.db.commit)
        return {"summary": summary, "generated_by": summary_method}

    def _fallback_summary(self, candidate, skills_str: str) -> str:
        """Deterministic local generation if Gemini is unreachable."""
        return (
            f"{candidate.name} applied for {candidate.role_applied} "
            f"with skills: {skills_str}. Status: {candidate.status}."
        )
    
    
    def archieve_candidate(self,candidate_id:str)->Candidate:
        candidate=self.get_candidate(candidate_id)
        if candidate is None:
            raise ValueError("Candidate Not Found")
        
        candidate.status=CandidateStatus.archived
        candidate.deleted_at=datetime.utcnow()
        self.db.commit()
        self.db.refresh(candidate)
        return candidate