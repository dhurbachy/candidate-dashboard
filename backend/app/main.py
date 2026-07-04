from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine,Base,SessionLocal
from app.models import Base,User,Role,Candidate,CandidateStatus
from app.auth import get_password_hash

def bootstrap_mock_data():
    """Seeds Only runs if the users table is empty and call on
    every startup."""
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        admin = User(
            email="admin@techkraft.dev",
            password=get_password_hash("admin12345"),
            role=Role.admin,
        )
        reviewer = User(
            email="reviewer@techkraft.dev",
            password=get_password_hash("reviewer12345"),
            role=Role.reviewer,
        )
        db.add_all([admin, reviewer])

        db.add_all([
            Candidate(
                name="Ada Lovelace",
                email="ada@example.com",
                role_applied="Backend Engineer",
                status=CandidateStatus.new,
                skills=["python", "sql"],
                internal_notes="Strong referral from engineering lead.",
            ),
            Candidate(
                name="Grace Hopper",
                email="grace@example.com",
                role_applied="Full Stack Engineer",
                status=CandidateStatus.new,
                skills=["python", "react", "typescript"],
                internal_notes=None,
            ),
        ])

        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app:FastAPI):
   Base.metadata.create_all(bind=engine)
   print("[STARTUP] database initialized successfully.")
   yield
   print("[SHUTDOWN] Application  resources Cleanup.")

app=FastAPI(title="Candidate Dashboard")

@app.get("/health")
def health():
    """
    Server Operational Verfication
    """
    return {"status":"operational"}