from fastapi import FastAPI

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import triage_message

app = FastAPI()


@app.get("/")
def root():
    return {"message": "LLM Support Triage API is running"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    return triage_message(request.message)
