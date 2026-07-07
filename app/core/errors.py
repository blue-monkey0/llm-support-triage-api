from enum import Enum


class ErrorCode(str, Enum):
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    LLM_PARSE_ERROR = "LLM_PARSE_ERROR"
    LLM_SCHEMA_ERROR = "LLM_SCHEMA_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)
