import datetime
from sqlalchemy import Column,Integer,Boolean,String, ForeignKey,DateTime,Index,UniqueConstraint,CheckConstraint
from sqlalchemy.orm import relationship,declarative_base
import enum
from app.database import Base

from sqlalchemy.types import JSON

# Base=declarative_base()

class User(Base):
    """
    Represents users
    """

    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True, index=True, nullable=False)
    password=Column(String,nullable=False)

    role=Column(String,nullable=False)
    deleted_at=Column(DateTime,nullable=True,default=None)
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

class Candidate(Base):
    """
    Represents job candidate tracking records
    """
    __tablename__="candidates"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String,nullable=False)
    email=Column(String,unique=True, index=True, nullable=False)
    role_applied=Column(String,nullable=False)
    skills=Column(JSON, nullable=False,default=list)
    created_at=Column(DateTime,default=datetime.datetime.utcnow)
    status=Column(String, default="active",index=True,nullable=False)
    internal_notes=Column(String, nullable=True)
    ai_summary=Column(String, nullable=True)
    ai_status=Column(String, default="idle",nullable=False)
    scores=relationship("Score",back_populates="candidate",cascade="all, delete-orphan")
    deleted_at=Column(DateTime,nullable=True,default=None,index=True)

    __table_args__=(Index("idx_candidates_lookup","status","role_applied"),)

class Score(Base):
    """""
    Represents Evaluation Score Cards attached to candidate targets
    """""

    __tablename__="scores"

    id=Column(Integer, primary_key=True,index=True)
    candidate_id=Column(Integer, ForeignKey("candidates.id"),nullable=False)
    reviewer_id=Column(Integer, ForeignKey("users.id"),nullable=False)
    category=Column(String,nullable=False)
    rating=Column(Integer,nullable=False)
    note=Column(String, nullable=True)
    created_at=Column(DateTime, default=datetime.datetime.utcnow)

    candidate=relationship("Candidate", back_populates="scores")
    reviewer=relationship("User")

    __table_args__ = (
        UniqueConstraint('candidate_id', 'reviewer_id', 'category', name='_candidate_reviewer_category_uc'),
        CheckConstraint(
            'rating >= 1 AND rating <= 5', 
            name='check_rating_range_boundary'
        ),
        CheckConstraint(
            "length(trim(category)) > 0", 
            name='check_category_not_empty'
        )
    )

class CandidateStatus(str, enum.Enum):
    new = "new"
    reviewed = "reviewed"
    hired = "hired"
    rejected = "rejected"
    archived = "archived"  

class Role(str, enum.Enum):
    reviewer = "reviewer"
    admin = "admin"

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)

    user = relationship("User", back_populates="refresh_tokens")