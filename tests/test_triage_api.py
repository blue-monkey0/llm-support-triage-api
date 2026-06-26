from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app as fastapi_app
from app.schemas.triage import TriageResponse

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


def test_triage_requires_message_field():
    response = client.post(
        "/triage",
        json={"text": "Payment is failing"},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_triage_endpoint_with_mocked_response(monkeypatch):
    def fake_triage_message(message: str) -> TriageResponse:
        return TriageResponse(
            category="payment",
            severity="critical",
            summary="Payment issue detected.",
            next_action="Check payment gateway logs.",
        )

    monkeypatch.setattr(main_module, "triage_message", fake_triage_message)

    response = client.post(
        "/triage",
        json={"message": "Payment is failing for all users after checkout"},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["category"] in ALLOWED_CATEGORIES
    assert response_json["severity"] in ALLOWED_SEVERITIES
    assert isinstance(response_json["summary"], str)
    assert isinstance(response_json["next_action"], str)

    assert response_json == {
        "category": "payment",
        "severity": "critical",
        "summary": "Payment issue detected.",
        "next_action": "Check payment gateway logs.",
    }
