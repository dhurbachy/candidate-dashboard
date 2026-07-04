from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):

    yield
    
app=FastAPI(title="Candidate Dashboard")

@app.get("/health")
def health():
    """
    Server Operational Verfication
    """
    return {"status":"operational"}