from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ErrorResponse, ResponseMetadata


class TriageRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="Customer support message to classify and summarise",
    )


class TriageResult(BaseModel):
    category: Literal[
        "authentication",
        "payment",
        "performance",
        "deployment",
        "integration",
        "general",
    ] = Field(..., description="Normalized support issue category.")

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = Field(..., description="Normalized operational severity.")

    summary: str = Field(..., description="Concise summary of the customer issue.")
    next_action: str = Field(..., description="Recommended next operational action.")


class TriageResponse(BaseModel):
    status: Literal["success", "fallback", "error"] = Field(
        ..., description="Processing status of the triage request."
    )
    data: Optional[TriageResult] = Field(
        default=None,
        description="Validated triage result. Null when status is fallback or error.",
    )
    error: Optional[ErrorResponse] = Field(
        default=None,
        description="Structured error details. Null when status is success.",
    )
    metadata: ResponseMetadata = Field(
        ..., description="Request-scoped operational metadata."
    )
