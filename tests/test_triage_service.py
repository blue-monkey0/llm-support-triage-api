import pytest

from app.core.errors import AppError, ErrorCode
from app.services.triage_service import parse_llm_json_response, triage_message


class FakeLLMClient:
    def __init__(
        self, response_text: str | None = None, error: Exception | None = None
    ):
        self.response_text = response_text
        self.error = error
        self.received_prompt = None

    def generate_content(self, prompt: str) -> str:
        self.received_prompt = prompt

        if self.error:
            raise self.error

        return self.response_text or ""


def test_parse_llm_json_response_accepts_markdown_json_block():
    response_text = """
```json
{
  "category": "payment",
  "severity": "critical",
  "summary": "Payment failure.",
  "next_action": "Check payment gateway logs."
}
```
"""

    parsed_response = parse_llm_json_response(response_text)

    assert parsed_response["category"] == "payment"
    assert parsed_response["severity"] == "critical"


def test_triage_message_returns_validated_result_with_normalized_values():
    fake_client = FakeLLMClient(response_text="""
{
  "category": "billing",
  "severity": "urgent",
  "summary": "Checkout payments are failing.",
  "next_action": "Review the payment provider dashboard."
}
""")

    result = triage_message("Payment is failing after checkout.", fake_client)

    assert "Payment is failing after checkout." in fake_client.received_prompt
    assert result.category == "payment"
    assert result.severity == "medium"
    assert result.summary == "Checkout payments are failing."
    assert result.next_action == "Review the payment provider dashboard."


def test_triage_message_raises_provider_error_when_llm_client_fails():
    fake_client = FakeLLMClient(error=RuntimeError("provider unavailable"))

    with pytest.raises(AppError) as exc_info:
        triage_message("Payment is failing after checkout.", fake_client)

    assert exc_info.value.code == ErrorCode.LLM_PROVIDER_ERROR
    assert exc_info.value.message == "The upstream LLM provider returned an error."


def test_triage_message_raises_parse_error_for_invalid_json():
    fake_client = FakeLLMClient(response_text="not json")

    with pytest.raises(AppError) as exc_info:
        triage_message("Payment is failing after checkout.", fake_client)

    assert exc_info.value.code == ErrorCode.LLM_PARSE_ERROR
    assert (
        exc_info.value.message
        == "The model response could not be parsed as valid JSON."
    )


def test_triage_message_raises_schema_error_for_missing_required_fields():
    fake_client = FakeLLMClient(response_text="""
{
  "category": "payment",
  "severity": "critical",
  "summary": "Payment failure."
}
""")

    with pytest.raises(AppError) as exc_info:
        triage_message("Payment is failing after checkout.", fake_client)

    assert exc_info.value.code == ErrorCode.LLM_SCHEMA_ERROR
    assert (
        exc_info.value.message
        == "The model response is missing one or more required fields."
    )
