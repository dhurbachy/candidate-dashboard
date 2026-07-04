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
    