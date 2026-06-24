import logging

from fastapi import FastAPI

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import triage_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "LLM Support Triage API is running"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    return triage_message(request.message)
