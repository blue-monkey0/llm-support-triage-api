from typing import Optional

from pydantic import BaseModel, Field

from app.core.errors import ErrorCode


class ErrorResponse(BaseModel):
    code: ErrorCode = Field(
        ..., description="Machine-readable error code used by clients for control flow."
    )
    message: str = Field(
        ...,
        description="Human-readable error message for debugging and operational context.",
    )


class ResponseMetadata(BaseModel):
    request_id: str = Field(
        ..., description="Unique identifier for tracing a single API request."
    )
    model: Optional[str] = Field(
        default=None, description="LLM model used to process the request."
    )
    latency_ms: Optional[int] = Field(
        default=None, description="End-to-end processing latency in milliseconds."
    )
