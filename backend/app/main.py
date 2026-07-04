from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine,Base
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