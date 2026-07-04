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

