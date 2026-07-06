import logging
import time
from uuid import uuid4

from fastapi import FastAPI

from app.core.errors import AppError, ErrorCode
from app.schemas.common import ErrorResponse, ResponseMetadata
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import GEMINI_MODEL, triage_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Support Triage API",
    description="API for classifying support message into operational triage categories.",
    version="0.2.0",
)


@app.get("/health_check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "LLM Support Triage API is running"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest) -> TriageResponse:
    start_time = time.perf_counter()
    request_id = f"req_{uuid4().hex}"

    try:
        result = triage_message(request.message)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        return TriageResponse(
            status="success",
            data=result,
            error=None,
            metadata=ResponseMetadata(
                request_id=request_id, model=GEMINI_MODEL, latency_ms=latency_ms
            ),
        )

    except AppError as exc:
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.warning(
            "Triage request returned fallback response.",
            extra={
                "request_id": request_id,
                "model": GEMINI_MODEL,
                "latency_ms": latency_ms,
            },
        )
        return TriageResponse(
            status="fallback",
            data=None,
            error=ErrorResponse(code=exc.code, message=exc.message),
            metadata=ResponseMetadata(
                request_id=request_id, model=GEMINI_MODEL, latency_ms=latency_ms
            ),
        )

    except Exception:
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.exception(
            "Unexpected triage request failure",
            extra={
                "request_id": request_id,
                "error_code": ErrorCode.INTERNAL_ERROR,
                "latency_ms": latency_ms,
            },
        )

        return TriageResponse(
            status="error",
            data=None,
            error=ErrorResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message="Unexpected server error occured.",
            ),
            metadata=ResponseMetadata(
                request_id=request_id, model=GEMINI_MODEL, latency_ms=latency_ms
            ),
        )
