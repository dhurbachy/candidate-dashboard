from fastapi import FastAPI

app=FastAPI(title="Candidate Dashboard")

@app.get("/health")
def health():
    """
    Server Operational Verfication
    """
    return {"status":"operational"}