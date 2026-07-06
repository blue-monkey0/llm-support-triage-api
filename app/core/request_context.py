from uuid import uuid4

from fastapi import Request

REQUEST_ID_HEADER = "x-request-id"


def generate_request_id() -> str:
    return f"req_{uuid4().hex}"


def get_request_id(request: Request) -> str:
    return request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
