from typing import Literal

from pydantic import BaseModel


class TriageRequest(BaseModel):
    message: str


class TriageResponse(BaseModel):
    category: Literal[
        "authentication",
        "payment",
        "performance",
        "deployment",
        "integration",
        "general",
    ]
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    summary: str
    next_action: str
