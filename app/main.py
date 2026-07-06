import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.clients.gemini_client import GEMINI_MODEL
from app.core.errors import AppError, ErrorCode
from app.core.request_context import get_request_id
from app.schemas.common import ErrorResponse, ResponseMetadata
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import triage_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Support Triage API",
    description="API for classifying support messages into operational triage categories.",
    version="0.2.0",
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.warning(
        "Request validation failed path=%s request_id=%s error_code=%s errors=%s",
        request.url.path,
        request_id,
        ErrorCode.VALIDATION_ERROR,
        exc.errors(),
    )

    response = TriageResponse(
        status="error",
        data=None,
        error=ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed.",
        ),
        metadata=ResponseMetadata(
            request_id=request_id,
            model=None,
            latency_ms=None,
        ),
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode="json"),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "LLM Support Triage API is running"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: Request, payload: TriageRequest) -> TriageResponse:
    start_time = time.perf_counter()
    request_id = get_request_id(request)

    try:
        result = triage_message(payload.message)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.info(
            "Triage request succeeded request_id=%s latency_ms=%s model=%s",
            request_id,
            latency_ms,
            GEMINI_MODEL,
        )

        return TriageResponse(
            status="success",
            data=result,
            error=None,
            metadata=ResponseMetadata(
                request_id=request_id,
                model=GEMINI_MODEL,
                latency_ms=latency_ms,
            ),
        )

    except AppError as exc:
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.warning(
            "Triage request returned fallback response request_id=%s error_code=%s latency_ms=%s",
            request_id,
            exc.code,
            latency_ms,
        )

        return TriageResponse(
            status="fallback",
            data=None,
            error=ErrorResponse(
                code=exc.code,
                message=exc.message,
            ),
            metadata=ResponseMetadata(
                request_id=request_id,
                model=GEMINI_MODEL,
                latency_ms=latency_ms,
            ),
        )

    except Exception:
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.exception(
            "Unexpected triage request failure request_id=%s error_code=%s latency_ms=%s",
            request_id,
            ErrorCode.INTERNAL_ERROR,
            latency_ms,
        )

        return TriageResponse(
            status="error",
            data=None,
            error=ErrorResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message="Unexpected server error occurred.",
            ),
            metadata=ResponseMetadata(
                request_id=request_id,
                model=GEMINI_MODEL,
                latency_ms=latency_ms,
            ),
        )
