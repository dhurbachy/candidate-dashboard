from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, conint

from .models import Role, CandidateStatus



class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True



class ScoreCreate(BaseModel):
    category: str
    score: conint(ge=1, le=5)
    note: Optional[str] = None


class ScoreOut(BaseModel):
    id: int
    candidate_id: int
    category: str
    rating: int
    reviewer_id: int
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_applied: str
    status: CandidateStatus
    skills: List[str]
    created_at: datetime
    ai_summary: Optional[str] = None
    internal_notes: Optional[str] = None  

    class Config:
        from_attributes = True


class CandidateListItem(BaseModel):
    id: int
    name: str
    role_applied: str
    status: CandidateStatus
    skills: List[str]

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    items: List[CandidateListItem]
    total: int
    page: int
    page_size: int


class CandidateDetailResponse(BaseModel):
    candidate: CandidateOut
    scores: List[ScoreOut]
    # scores:int


class GeminiSummaryData(BaseModel):
    """Schema matching the inner Gemini response dictionary."""
    summary: str
    generated_by: str

class SummaryResponse(BaseModel):
    status: str 
    summary: GeminiSummaryData