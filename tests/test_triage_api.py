from fastapi.testclient import TestClient

import app.main as main_module
from app.core.errors import AppError, ErrorCode
from app.main import app as fastapi_app
from app.schemas.triage import TriageResult

client = TestClient(fastapi_app)

ALLOWED_CATEGORIES = {
    "authentication",
    "payment",
    "performance",
    "deployment",
    "integration",
    "general",
}

ALLOWED_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "LLM Support Triage API is running"}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_requires_message_field_with_v2_error_envelope():
    response = client.post(
        "/triage",
        headers={"x-request-id": "req_validation_test_001"},
        json={"text": "Payment is failing"},
    )

    assert response.status_code == 422

    response_json = response.json()

    assert response_json["status"] == "error"
    assert response_json["data"] is None
    assert response_json["error"] == {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed.",
    }
    assert response_json["metadata"] == {
        "request_id": "req_validation_test_001",
        "model": None,
        "latency_ms": None,
    }


def test_triage_rejects_empty_message_with_v2_error_envelope():
    response = client.post(
        "/triage",
        headers={"x-request-id": "req_empty_message_test_001"},
        json={"message": ""},
    )

    assert response.status_code == 422

    response_json = response.json()

    assert response_json["status"] == "error"
    assert response_json["data"] is None
    assert response_json["error"]["code"] == "VALIDATION_ERROR"
    assert response_json["metadata"]["request_id"] == "req_empty_message_test_001"


def test_triage_endpoint_with_mocked_success_response(monkeypatch):
    def fake_triage_message(message: str) -> TriageResult:
        return TriageResult(
            category="payment",
            severity="critical",
            summary="Payment issue detected.",
            next_action="Check payment gateway logs.",
        )

    monkeypatch.setattr(main_module, "triage_message", fake_triage_message)

    response = client.post(
        "/triage",
        headers={"x-request-id": "req_success_test_001"},
        json={"message": "Payment is failing for all users after checkout"},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["status"] == "success"
    assert response_json["error"] is None
    assert response_json["data"]["category"] in ALLOWED_CATEGORIES
    assert response_json["data"]["severity"] in ALLOWED_SEVERITIES
    assert isinstance(response_json["data"]["summary"], str)
    assert isinstance(response_json["data"]["next_action"], str)
    assert response_json["metadata"]["request_id"] == "req_success_test_001"
    assert response_json["metadata"]["model"] == main_module.GEMINI_MODEL
    assert isinstance(response_json["metadata"]["latency_ms"], int)

    assert response_json["data"] == {
        "category": "payment",
        "severity": "critical",
        "summary": "Payment issue detected.",
        "next_action": "Check payment gateway logs.",
    }


def test_triage_generates_request_id_when_header_is_missing(monkeypatch):
    def fake_triage_message(message: str) -> TriageResult:
        return TriageResult(
            category="general",
            severity="low",
            summary="General support issue.",
            next_action="Review the support message.",
        )

    monkeypatch.setattr(main_module, "triage_message", fake_triage_message)

    response = client.post(
        "/triage",
        json={"message": "I need help with my account."},
    )

    assert response.status_code == 200

    request_id = response.json()["metadata"]["request_id"]

    assert request_id.startswith("req_")
    assert len(request_id) > len("req_")


def test_triage_returns_fallback_envelope_for_app_error(monkeypatch):
    def fake_triage_message(message: str) -> TriageResult:
        raise AppError(
            code=ErrorCode.LLM_PARSE_ERROR,
            message="The model response could not be parsed as valid JSON.",
        )

    monkeypatch.setattr(main_module, "triage_message", fake_triage_message)

    response = client.post(
        "/triage",
        headers={"x-request-id": "req_fallback_test_001"},
        json={"message": "Payment is failing for all users after checkout"},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["status"] == "fallback"
    assert response_json["data"] is None
    assert response_json["error"] == {
        "code": "LLM_PARSE_ERROR",
        "message": "The model response could not be parsed as valid JSON.",
    }
    assert response_json["metadata"]["request_id"] == "req_fallback_test_001"
    assert response_json["metadata"]["model"] == main_module.GEMINI_MODEL
    assert isinstance(response_json["metadata"]["latency_ms"], int)


def test_triage_returns_error_envelope_for_unexpected_error(monkeypatch):
    def fake_triage_message(message: str) -> TriageResult:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(main_module, "triage_message", fake_triage_message)

    response = client.post(
        "/triage",
        headers={"x-request-id": "req_internal_error_test_001"},
        json={"message": "Payment is failing for all users after checkout"},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["status"] == "error"
    assert response_json["data"] is None
    assert response_json["error"] == {
        "code": "INTERNAL_ERROR",
        "message": "Unexpected server error occurred.",
    }
    assert response_json["metadata"]["request_id"] == "req_internal_error_test_001"
