import json
import logging

from google import genai

from app.config import GEMINI_API_KEY
from app.schemas.triage import TriageResponse

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

CATEGORY_ALIASES = {
    "authentication": "authentication",
    "auth": "authentication",
    "login": "authentication",
    "signin": "authentication",
    "sign-in": "authentication",
    "sso": "authentication",
    "oauth": "authentication",
    "token": "authentication",
    "session": "authentication",
    "permission": "authentication",
    "unauthorized": "authentication",
    "forbidden": "authentication",
    "payment": "payment",
    "payments": "payment",
    "billing": "payment",
    "checkout": "payment",
    "invoice": "payment",
    "performance": "performance",
    "latency": "performance",
    "slow": "performance",
    "timeout": "performance",
    "deployment": "deployment",
    "deploy": "deployment",
    "release": "deployment",
    "rollback": "deployment",
    "integration": "integration",
    "third-party": "integration",
    "webhook": "integration",
    "api integration": "integration",
    "general": "general",
}

ALLOWED_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def normalize_category(category: str) -> str:
    normalized = category.strip().lower()

    if normalized in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[normalized]

    logger.warning("Unknown category received: %s", category)

    return "general"


def normalize_severity(severity: str) -> str:
    normalized = severity.strip().lower()

    if normalized in ALLOWED_SEVERITIES:
        return normalized

    logger.warning("Unknown severity received: %s", severity)

    return "medium"


def parse_llm_json_response(response_text: str) -> dict:
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return json.loads(cleaned_text)


def fallback_triage_response() -> TriageResponse:
    return TriageResponse(
        category="general",
        severity="low",
        summary="LLM triage failed. Returning fallback response.",
        next_action="Review the customer message manually.",
    )


def triage_message(message: str) -> TriageResponse:
    prompt = f"""
You are a support triage assistant.

Analyze the customer issue.

Customer message:
{message}

Return only valid JSON.
Do not include markdown.
Do not include explanation.

Use only one of these category values:
authentication, payment, performance, deployment, integration, general

Use only one of these severity values:
low, medium, high, critical

JSON schema:
{{
  "category": "authentication | payment | performance | deployment | integration | general",
  "severity": "low | medium | high | critical",
  "summary": "string",
  "next_action": "string"
}}
"""

    try:
        logger.info("Calling Gemini API for triage")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        logger.info("Gemini API call succeeded")

        parsed_response = parse_llm_json_response(response.text)

        category = normalize_category(parsed_response["category"])
        severity = normalize_severity(parsed_response["severity"])

        return TriageResponse(
            category=category,
            severity=severity,
            summary=parsed_response["summary"],
            next_action=parsed_response["next_action"],
        )

    except Exception:
        logger.exception("Gemini triage failed")
        return fallback_triage_response()
