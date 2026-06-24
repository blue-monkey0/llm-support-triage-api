from pydantic import BaseModel


class TriageRequest(BaseModel):
    message: str


class TriageResponse(BaseModel):
    category: str
    severity: str
    summary: str
    next_action: str
