import json
import logging

from app.clients.gemini_client import GeminiClient
from app.core.errors import AppError, ErrorCode
from app.schemas.triage import TriageResult

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


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


def build_triage_prompt(message: str) -> str:
    return f"""
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


def triage_message(
    message: str, llm_client: GeminiClient | None = None
) -> TriageResult:
    client = llm_client or GeminiClient()
    prompt = build_triage_prompt(message)

    try:
        response_text = client.generate_content(prompt)

    except Exception as exc:
        logger.exception("Gemini API call failed")
        raise AppError(
            code=ErrorCode.LLM_PROVIDER_ERROR,
            message="The upstream LLM provider returned an error.",
        ) from exc

    try:
        parsed_response = parse_llm_json_response(response_text)

    except json.JSONDecodeError as exc:
        logger.exception("Failed to parse Gemini response as JSON.")
        raise AppError(
            code=ErrorCode.LLM_PARSE_ERROR,
            message="The model response could not be parsed as valid JSON.",
        ) from exc

    try:
        category = normalize_category(parsed_response["category"])
        severity = normalize_severity(parsed_response["severity"])

        return TriageResult(
            category=category,
            severity=severity,
            summary=parsed_response["summary"],
            next_action=parsed_response["next_action"],
        )

    except KeyError as exc:
        logger.exception("Gemini response is missing required fields.")
        raise AppError(
            code=ErrorCode.LLM_SCHEMA_ERROR,
            message="The model response is missing one or more required fields.",
        ) from exc
