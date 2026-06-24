import json

from google import genai

from app.config import GEMINI_API_KEY
from app.schemas.triage import TriageResponse

client = genai.Client(api_key=GEMINI_API_KEY)


def triage_message(message: str) -> TriageResponse:
    prompt = f"""
You are a support triage assistant.

Analyze the customer issue.

Customer message:
{message}

Return only valid JSON.
Do not include markdown.
Do not include explanation.

JSON schema:
{{
  "category": "authentication | payment | performance | deployment | integration | general",
  "severity": "low | medium | high | critical",
  "summary": "string",
  "next_action": "string"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        parsed_response = json.loads(response.text)

        return TriageResponse(
            category=parsed_response["category"],
            severity=parsed_response["severity"],
            summary=parsed_response["summary"],
            next_action=parsed_response["next_action"],
        )

    except Exception:
        return TriageResponse(
            category="general",
            severity="low",
            summary="LLM triage failed. Returning fallback response.",
            next_action="Review the customer message manually.",
        )
