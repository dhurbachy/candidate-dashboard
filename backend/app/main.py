import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.genai.types import HttpOptions, HttpRetryOptions
from app.database import engine, SessionLocal
from app.models import Base, User, Candidate, Role, CandidateStatus
from app.auth import get_password_hash
from app.routers import candidate, auth as auth_router
from app.logging import logger
from google import genai
from app.config import settings

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
        logger.info("Bootstrapped mock data")

    finally:
        db.close()

class GeminiClientContainer:

    def __init__(self):
        self._client = None

    def get_client(self) -> genai.Client:
        if self._client is None:
            retry_config = HttpRetryOptions(
                attempts=3,          # Cap attempts at 3 to protect your token budget
                initial_delay=1.0,      # Start with a 1-second pause
                max_delay=10.0,         # Never freeze the thread longer than 10 seconds
            )
            options = HttpOptions(retry_options=retry_config)
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    async def close(self):
        if self._client and hasattr(self._client, "aclose"):
            try:
                await self._client.aclose()
            except Exception:
                pass 
@asynccontextmanager
async def lifespan(app:FastAPI):
   logger.info("Starting up the application")
   Base.metadata.create_all(bind=engine)
   bootstrap_mock_data()
   container = GeminiClientContainer()
   app.state.gemini_container = container
   yield
   await container.close()

   logger.info("SIGTERM/SIGINT signal intercepted. Initiating graceful engine shutdown...")
   engine.dispose()
   logger.info("Database connection pools drained successfully. Application offline.")

app=FastAPI(title="Candidate Dashboard",lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router.router,prefix="/api")
app.include_router(candidate.router,prefix="/api")

@app.exception_handler(Exception)
async def catchall_error_boundary(request: Request, exc: Exception):
    logger.error(
        f"Uncaught critical panic exception on route {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal operational error occurred"},
    )

@app.get("/health")
def health():
    """
    Server Operational Verfication
    """
    return {"status":"operational"}