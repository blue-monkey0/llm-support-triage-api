from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TriageRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "LLM Support Triage API is running"}


@app.post("/triage")
def triage(request: TriageRequest):
    message = request.message.lower()

    if "login" in message:
        category = "authentication"
        severity = "high"
        summary = "Login-related issue detected."
        next_action = "Check authentication service logs and recent deployments."

    elif "payment" in message:
        category = "payment"
        severity = "high"
        summary = "Payment-related issue detected."
        next_action = "Check payment gateway status and transaction logs."

    elif "slow" in message or "latency" in message:
        category = "performance"
        severity = "medium"
        summary = "Performance-related issue detected"
        next_action = "Check API latency metrics and server resource usage."

    else:
        category = "general"
        severity = "slow"
        summary = "General support issue detected."
        next_action = "Review the customer message and assign it to the support team."

    return {
        "category": category,
        "severity": severity,
        "summary": summary,
        "next_action": next_action,
    }
