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
   

@router.post("/{candidate_id}/summary",response_model=SummaryResponse)
async def trigger_summary(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request=None,
):
    
    client = request.app.state.gemini_container.get_client()
    service = CandidateService(db,gemini_client=client)
    try:
        summary = await service.generate_summary(candidate_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SummaryResponse(status="ready", summary=summary)
 
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def archive_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Admin-only. Always a soft delete - see CandidateService.archive_candidate.
    if current_user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
 
    service = CandidateService(db)
    try:
        service.archieve_candidate(candidate_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

@router.get("/stream/scores", response_class=StreamingResponse)
async def stream_live_score_cards(
    current_user: dict = Depends(get_current_user)
):
    """
    Real-time Server-Sent Events (SSE) telemetry data pipeline.
    Streams active assessment updates dynamically over a long-lived HTTP connection.
    """
    async def sse_event_generator():
        listener = score_broadcaster.subscribe()
        
        try:
            while True:
                try:
                    event = await asyncio.wait_for(listener.__anext__(), timeout=15.0)
                    yield event
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except (asyncio.CancelledError, StopAsyncIteration):
            pass

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" 
        }
    )