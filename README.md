# LLM Support Triage API

HTTP API for classifying customer support messages into operational triage categories using an LLM-backed processing pipeline.

The service accepts a support message, calls Gemini through an isolated provider client, validates and normalizes the model output, and returns a stable response envelope for downstream consumers.

---

## Overview

`llm-support-triage-api` provides a triage endpoint for support automation workflows.

Given a customer support message, the API returns:

* normalized issue category
* normalized severity
* concise issue summary
* recommended next operational action
* request-scoped metadata
* structured error details for fallback or failure scenarios

The API is designed to make LLM output safer and easier to consume from backend services, support dashboards, internal tools, and automation pipelines.

---

## Key Capabilities

* FastAPI HTTP API
* Gemini API integration through an isolated client layer
* Pydantic request validation
* Pydantic response validation
* Stable v2 response envelope
* Explicit success, fallback, and error states
* Machine-readable error codes
* Category normalization
* Severity normalization
* JSON parsing guard for LLM responses
* Request-level metadata
* Request ID generation
* Latency measurement
* Logging for operational troubleshooting
* Pytest-based API tests
* Mockable LLM client interface
* Docker-based local runtime
* Environment variable injection through `.env`

---

## Tech Stack

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* Gemini API
* python-dotenv
* pytest
* FastAPI TestClient
* Black
* isort
* Docker
* Mermaid

---

## Project Structure

```text
llm-support-triage-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── clients/
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── errors.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   └── triage.py
│   └── services/
│       ├── __init__.py
│       └── triage_service.py
├── tests/
│   └── test_triage_api.py
├── Dockerfile
├── .dockerignore
├── README.md
├── requirements.txt
├── .gitignore
└── .env
```

> `.env` is used for local development and should not be committed to source control.

---

## Architecture

### Layer Responsibilities

| Layer         | Path                             | Responsibility                                                                              |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------------------- |
| API layer     | `app/main.py`                    | Handles HTTP requests, creates response envelopes, and exposes endpoints.                   |
| Service layer | `app/services/triage_service.py` | Builds prompts, parses LLM output, normalizes values, and returns validated triage results. |
| Client layer  | `app/clients/gemini_client.py`   | Owns direct communication with Gemini API.                                                  |
| Schema layer  | `app/schemas/`                   | Defines request, response, result, error, and metadata contracts.                           |
| Core layer    | `app/core/`                      | Defines shared application errors and error codes.                                          |

---

### Request Flow

```mermaid
flowchart LR
    Client[Client / Swagger UI / curl] --> FastAPI[FastAPI App]
    FastAPI --> Validation[Pydantic Request Validation]
    Validation --> Endpoint[API Endpoint]
    Endpoint --> Service[Triage Service]
    Service --> GeminiClient[Gemini Client]
    GeminiClient --> Gemini[Gemini API]
    Gemini --> GeminiClient
    GeminiClient --> Service
    Service --> Parsing[JSON Parsing]
    Parsing --> Normalization[Category and Severity Normalization]
    Normalization --> Result[TriageResult]
    Result --> Envelope[TriageResponse Envelope]
    Envelope --> Client
```

The API receives a support message from a client, validates the request body, sends the message to the triage service, calls Gemini through the provider client, parses the model response, normalizes category and severity values, and returns a stable response envelope.

---

### Fallback Flow

```mermaid
flowchart LR
    Service[Triage Service] --> GeminiClient[Gemini Client]
    GeminiClient --> Gemini[Gemini API]
    Gemini --> Failure[Provider / Parse / Schema Failure]
    Failure --> AppError[AppError with ErrorCode]
    AppError --> Endpoint[API Endpoint]
    Endpoint --> Envelope[Fallback Response Envelope]
    Envelope --> Client[Client]
```

The service raises an application-level error when the LLM provider fails, the model response cannot be parsed, or the response does not match the expected schema.

The endpoint converts that application error into a structured fallback response.

---

## API Endpoints

### `GET /`

Basic service check.

#### Response

```json
{
  "message": "LLM Support Triage API is running"
}
```

---

### `GET /health`

Health check endpoint.

#### Response

```json
{
  "status": "ok"
}
```

This endpoint verifies that the API process is running and can respond to requests.

---

### `POST /triage`

Classifies a customer support message and returns a structured triage response.

#### Request Body

```json
{
  "message": "Users cannot log in with SSO after the latest deployment."
}
```

#### Success Response

```json
{
  "status": "success",
  "data": {
    "category": "authentication",
    "severity": "high",
    "summary": "Users cannot log in with SSO after the latest deployment.",
    "next_action": "Check SSO provider logs, validate token claims, and review authentication-related deployment changes."
  },
  "error": null,
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 842
  }
}
```

---

## Response Contract

The `/triage` endpoint returns a stable response envelope.

Clients should branch on `status` first and use `error.code` for programmatic error handling.

### Top-Level Fields

| Field      | Type           | Description                                                               |
| ---------- | -------------- | ------------------------------------------------------------------------- |
| `status`   | string         | Processing status. One of `success`, `fallback`, or `error`.              |
| `data`     | object or null | Validated triage result. Present when `status` is `success`.              |
| `error`    | object or null | Structured error details. Present when `status` is `fallback` or `error`. |
| `metadata` | object         | Request-scoped operational metadata.                                      |

---

### `status`

Allowed values:

```text
success
fallback
error
```

| Status     | Meaning                                                                                           |
| ---------- | ------------------------------------------------------------------------------------------------- |
| `success`  | The service produced a validated triage result.                                                   |
| `fallback` | The service could not produce a validated LLM result and returned a controlled fallback response. |
| `error`    | The request failed due to an unexpected internal service error.                                   |

---

### `data`

`data` contains the validated triage result.

It is present only when `status` is `success`.

```json
{
  "category": "payment",
  "severity": "critical",
  "summary": "Checkout payments are failing for multiple users.",
  "next_action": "Check payment gateway health, recent deployment changes, and transaction failure logs."
}
```

#### Data Fields

| Field         | Type   | Description                            |
| ------------- | ------ | -------------------------------------- |
| `category`    | string | Normalized support issue category.     |
| `severity`    | string | Normalized operational severity.       |
| `summary`     | string | Concise summary of the customer issue. |
| `next_action` | string | Recommended next operational action.   |

---

### `error`

`error` contains structured failure details.

It is `null` when `status` is `success`.

```json
{
  "code": "LLM_PARSE_ERROR",
  "message": "The model response could not be parsed as valid JSON."
}
```

#### Error Fields

| Field     | Type   | Description                        |
| --------- | ------ | ---------------------------------- |
| `code`    | string | Machine-readable error code.       |
| `message` | string | Human-readable diagnostic message. |

Clients should use `error.code` for control flow.
Clients should not parse `error.message`.

---

### `metadata`

`metadata` contains request-scoped operational information.

```json
{
  "request_id": "req_9f1c2d...",
  "model": "gemini-2.5-flash",
  "latency_ms": 842
}
```

#### Metadata Fields

| Field        | Type            | Description                                     |
| ------------ | --------------- | ----------------------------------------------- |
| `request_id` | string          | Unique identifier for tracing a single request. |
| `model`      | string or null  | LLM model used for the request.                 |
| `latency_ms` | integer or null | End-to-end request latency in milliseconds.     |

---

## Allowed Categories

The API normalizes model output into one of the following category values:

```text
authentication
payment
performance
deployment
integration
general
```

### Category Examples

| Raw LLM Output | Normalized Category |
| -------------- | ------------------- |
| `auth`         | `authentication`    |
| `login`        | `authentication`    |
| `sso`          | `authentication`    |
| `billing`      | `payment`           |
| `payments`     | `payment`           |
| `checkout`     | `payment`           |
| `latency`      | `performance`       |
| `timeout`      | `performance`       |
| `deploy`       | `deployment`        |
| `rollback`     | `deployment`        |
| `webhook`      | `integration`       |
| `third-party`  | `integration`       |

Unknown category values are normalized to:

```text
general
```

---

## Allowed Severities

The API normalizes model output into one of the following severity values:

```text
low
medium
high
critical
```

Unknown severity values are normalized to:

```text
medium
```

This default is intentionally conservative. Returning `low` can hide important issues, while returning `critical` too often can create alert fatigue.

---

## Error Codes

| Code                 | Meaning                                                            | Typical Cause                                                    |
| -------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `LLM_PROVIDER_ERROR` | The upstream LLM provider failed.                                  | API key issue, provider outage, quota limit, or network failure. |
| `LLM_PARSE_ERROR`    | The model response could not be parsed as JSON.                    | Gemini returned prose, markdown, or malformed JSON.              |
| `LLM_SCHEMA_ERROR`   | The model response was JSON but did not match the expected schema. | Missing `category`, `severity`, `summary`, or `next_action`.     |
| `VALIDATION_ERROR`   | The request body failed validation.                                | Missing or empty `message` field.                                |
| `INTERNAL_ERROR`     | Unexpected server-side failure.                                    | Unhandled application error.                                     |

---

## Gemini Client

Gemini API access is isolated in `app/clients/gemini_client.py`.

The client layer owns provider-specific details such as:

* Gemini SDK client initialization
* model name
* provider request execution
* raw response text extraction
* provider-level logging

The service layer does not directly import or call the Gemini SDK.
It depends on a client interface that exposes `generate_content(prompt: str) -> str`.

This keeps the triage service focused on application logic:

* prompt construction
* response parsing
* response validation
* category normalization
* severity normalization
* domain result creation

This separation makes the service easier to test and reduces coupling between business logic and provider-specific implementation details.

---

## Example Requests

### curl

```bash
curl -X POST "http://127.0.0.1:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Users cannot log in with SSO after the latest deployment."
  }'
```

### Swagger UI

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

Use the `POST /triage` endpoint and provide the following request body:

```json
{
  "message": "Users cannot log in with SSO after the latest deployment."
}
```

Swagger UI and curl send the same underlying HTTP request when the method, URL, headers, and JSON body match.

---

## Example Responses

### Success

```json
{
  "status": "success",
  "data": {
    "category": "authentication",
    "severity": "high",
    "summary": "Users cannot log in with SSO after the latest deployment.",
    "next_action": "Check SSO provider logs, validate token claims, and review authentication-related deployment changes."
  },
  "error": null,
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 842
  }
}
```

### Fallback: Provider Error

```json
{
  "status": "fallback",
  "data": null,
  "error": {
    "code": "LLM_PROVIDER_ERROR",
    "message": "The upstream LLM provider returned an error."
  },
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 1032
  }
}
```

### Fallback: Parse Error

```json
{
  "status": "fallback",
  "data": null,
  "error": {
    "code": "LLM_PARSE_ERROR",
    "message": "The model response could not be parsed as valid JSON."
  },
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 917
  }
}
```

### Fallback: Schema Error

```json
{
  "status": "fallback",
  "data": null,
  "error": {
    "code": "LLM_SCHEMA_ERROR",
    "message": "The model response is missing one or more required fields."
  },
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 911
  }
}
```

### Internal Error

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Unexpected server error occurred."
  },
  "metadata": {
    "request_id": "req_9f1c2d...",
    "model": "gemini-2.5-flash",
    "latency_ms": 24
  }
}
```

---

## Reliability Design

### Request Validation

The request body is validated before endpoint logic is executed.

Valid request:

```json
{
  "message": "Login API returns 500 after deployment."
}
```

Invalid request:

```json
{
  "text": "Login API returns 500 after deployment."
}
```

Invalid requests are rejected by FastAPI/Pydantic validation before calling Gemini.

---

### Response Validation

The endpoint uses a Pydantic response model.

This ensures the API returns the documented response envelope:

```json
{
  "status": "success",
  "data": {
    "category": "authentication",
    "severity": "high",
    "summary": "...",
    "next_action": "..."
  },
  "error": null,
  "metadata": {
    "request_id": "req_...",
    "model": "gemini-2.5-flash",
    "latency_ms": 842
  }
}
```

---

### LLM Output Normalization

LLM outputs can vary even when prompted with a fixed schema.

The service normalizes category and severity values before returning a response.

This protects downstream consumers from minor wording variations in model output.

---

### Provider Isolation

Gemini-specific implementation details are isolated in the client layer.

This prevents the service layer from depending directly on provider SDK details and makes the codebase easier to adapt if the provider changes later.

For example, replacing Gemini with another LLM provider should primarily affect the client layer, not the triage service or API response contract.

---

### Fallback Handling

The service does not return fake successful triage data when LLM processing fails.

Instead, LLM failures are converted into fallback responses:

```json
{
  "status": "fallback",
  "data": null,
  "error": {
    "code": "LLM_PARSE_ERROR",
    "message": "The model response could not be parsed as valid JSON."
  },
  "metadata": {
    "request_id": "req_...",
    "model": "gemini-2.5-flash",
    "latency_ms": 932
  }
}
```

This allows clients to route fallback cases to manual review, retry, or operational monitoring workflows.

---

### Request Metadata

Each triage response includes request-scoped metadata.

The most important field is `request_id`.

Clients can use `request_id` when reporting issues, and operators can use the same ID to correlate logs for a specific request.

---

## Logging

The service uses Python logging to record runtime events.

Typical events include:

* Gemini API call started
* Gemini API call succeeded
* unknown category received
* unknown severity received
* LLM provider failure
* LLM parse failure
* LLM schema failure
* fallback response returned
* unexpected server error

Current log format:

```text
%(asctime)s %(levelname)s [%(name)s] %(message)s
```

Example:

```text
2026-06-30 20:30:00 WARNING [app.main] Triage request returned fallback response request_id=req_abc error_code=LLM_PARSE_ERROR latency_ms=932
```

---

## Testing

This project uses `pytest` and FastAPI's `TestClient`.

The tests should verify:

* `GET /` returns a successful response.
* `GET /health` returns `{"status": "ok"}`.
* `POST /triage` rejects invalid request bodies.
* `POST /triage` returns the v2 response envelope.
* success responses include `status`, `data`, `error`, and `metadata`.
* `data.category` is one of the allowed categories.
* `data.severity` is one of the allowed severities.
* fallback responses include a structured `error.code`.
* Gemini-dependent flows are mocked during tests.

---

## Why Mock the LLM Client in Tests?

The `/triage` endpoint depends on Gemini in the actual service flow.

Automated tests should not depend on:

* API keys
* external network availability
* Gemini quota limits
* Gemini response variability
* external API downtime
* additional API cost

The Gemini client should be mocked during tests so the test suite remains fast, deterministic, and reliable.

The service function accepts an optional LLM client dependency, which allows tests to inject a fake client without calling the real provider.

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/blue-monkey0/llm-support-triage-api.git
cd llm-support-triage-api
```

---

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

---

### 4. Create `.env`

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not commit `.env` to source control.

---

### 5. Run API Server

```bash
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Docker

### Build Image

```bash
docker build -t llm-support-triage-api .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env --name triage-api llm-support-triage-api
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Stop Container

```bash
docker stop triage-api
```

### Remove Container

```bash
docker rm triage-api
```

### Run in Detached Mode

```bash
docker run -d -p 8000:8000 --env-file .env --name triage-api llm-support-triage-api
```

View logs:

```bash
docker logs triage-api
```

---

## Docker Design Notes

### Base Image

The Docker image uses:

```dockerfile
FROM python:3.12-slim
```

This provides a lightweight Python 3.12 runtime.

---

### Working Directory

```dockerfile
WORKDIR /app
```

This sets `/app` as the working directory inside the container.

---

### Dependency Layer Caching

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
```

Dependencies are copied and installed before application code to improve Docker build caching.

If only application code changes, Docker can reuse the dependency installation layer.

---

### Runtime Host Binding

Inside Docker, Uvicorn should bind to all network interfaces:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Using `0.0.0.0` allows the host machine to reach the API through Docker port mapping.

---

### Secret Handling

Secrets such as `GEMINI_API_KEY` should not be baked into the Docker image.

Use runtime environment injection instead:

```bash
docker run --env-file .env ...
```

---

## Development Commands

### Run Server Locally

```bash
uvicorn app.main:app --reload
```

### Run Tests

```bash
python3 -m pytest
```

### Format Code

```bash
black app tests
```

### Sort Imports

```bash
isort app tests
```

### Format and Test

```bash
isort app tests
black app tests
python3 -m pytest
```

### Build Docker Image

```bash
docker build -t llm-support-triage-api .
```

### Run Docker Container

```bash
docker run -p 8000:8000 --env-file .env --name triage-api llm-support-triage-api
```

---

## Operational Notes

### Client Handling

Clients should branch on `status` first.

Recommended handling:

```text
if status == "success":
    consume data
elif status == "fallback":
    route to manual review or retry workflow
elif status == "error":
    treat as service failure
```

Clients should use `error.code` for programmatic handling.

Clients should not parse `error.message`.

---

### Fallback Semantics

Fallback responses indicate that the API server handled the request but could not produce a validated LLM triage result.

Typical fallback causes:

* LLM provider call failed
* LLM response was not valid JSON
* LLM response was missing required fields

Fallback responses should generally be routed to manual review, retry, or operational monitoring workflows.

---

### Request ID Usage

Each response includes `metadata.request_id`.

Use this value when investigating request-specific issues.

Example:

```text
request_id=req_9f1c2d...
```

This ID can be used to correlate API responses with server logs.

---

### Provider Client Boundary

Provider-specific code should remain inside `app/clients`.

The service layer should avoid importing provider SDKs directly.

This keeps the application easier to test, easier to maintain, and easier to migrate to another provider if needed.

---

## Version

Current API version:

```text
0.2.0
```

This version includes:

* v2 response envelope
* structured error object
* request metadata
* Gemini provider client isolation

---

## License

Internal development and demonstration use.
