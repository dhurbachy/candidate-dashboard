from typing import List, Optional
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status,Request
from sqlalchemy.orm import Session
from app.services.broadcaster import score_broadcaster
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.models import Candidate, Score,User,Role
from app.schemas import (
     CandidateListResponse,
    CandidateDetailResponse,
    ScoreCreate,
    ScoreOut,
    SummaryResponse,
)
from app.services.candidate import CandidateService
from app.auth import get_current_user, require_admin
from app.rate_limiter import rate_limit_ai_summary
from app.logging import logger

router = APIRouter(prefix="/candidates", tags=["Candidates Directory Engine"])

@router.get("", response_model=CandidateListResponse)
def get_all_candidates(
    status_filter: Optional[str] = Query(None,alias="status"),
    role_applied: Optional[str] = None,
    keyword: Optional[str] = None,
    skill:Optional[str]=None,
    page:int=Query(1,ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    service=CandidateService(db)
    items,total=service.list_candidates(status=status_filter,role_applied=role_applied,skill=skill,keyword=keyword,page=page,page_size=page_size)

    return CandidateListResponse(items=items,total=total,page=page,page_size=page_size)


@router.get("/{candidate_id}",response_model=CandidateDetailResponse)
def get_candidate_details(
    candidate_id: int, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    service=CandidateService(db)
    candidate=service.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
 
    candidate = service.redact_for_viewer(candidate, current_user)
    scores = service.get_scores_for_viewer(candidate_id, current_user)
    # scores=4
    return CandidateDetailResponse(candidate=candidate, scores=scores)
  
@router.post("/{candidate_id}/scores", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
async def submit_score(
     candidate_id: int,
    payload: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Attaches evaluation assessment scores cards.
    Guarantees clean connection isolation boundaries with automated transactional rolling-back.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Target candidate profile reference missing.")
    
    service = CandidateService(db)
    try:
        record = await service.add_score(
            candidate_id=candidate_id,
            reviewer=current_user,
            category=payload.category,
            score=payload.score,
            note=payload.note,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return record
   
