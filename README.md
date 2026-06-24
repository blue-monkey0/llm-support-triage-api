# LLM Support Triage API

A FastAPI-based backend service that uses Gemini API to classify customer support messages, estimate issue severity, summarize the issue, and recommend the next action.

This project is designed as a practical FDE-oriented AI backend project. Instead of building a simple chatbot, it focuses on turning an LLM use case into a production-aware API service.

## Problem

Support engineers often receive customer issues such as:

* Login failures
* Payment failures
* Slow API responses
* Deployment-related errors
* Third-party integration issues

Before solving the issue, engineers need to quickly understand:

1. What type of issue is this?
2. How severe is it?
3. What happened?
4. What should be checked first?

This process is called support triage.

## Solution

This API receives a customer support message and returns a structured triage result.

The response includes:

* `category`
* `severity`
* `summary`
* `next_action`

## Architecture

```text
Client / Swagger UI
        ↓
POST /triage
        ↓
FastAPI
        ↓
Pydantic Request Validation
        ↓
Gemini API
        ↓
JSON Parsing
        ↓
Response Normalization
        ↓
Pydantic Response Validation
        ↓
Structured API Response
```

## Current Features

* FastAPI server
* `POST /triage` endpoint
* Pydantic request validation
* Pydantic response schema validation
* Gemini API integration
* LLM-powered support ticket classification
* Structured JSON response generation
* Response normalization for category and severity
* Fallback response when LLM triage fails
* Logging for external API failures and abnormal responses
* Swagger UI API testing
* Black and isort formatting setup

## API Example

### Request

```json
{
  "message": "Payment is failing for all users after checkout"
}
```

### Response

```json
{
  "category": "payment",
  "severity": "critical",
  "summary": "All users are unable to complete payments after checkout.",
  "next_action": "Escalate to the on-call engineering team and investigate payment gateway logs and recent checkout-related deployments."
}
```

## Response Schema

| Field         | Type   | Description                |
| ------------- | ------ | -------------------------- |
| `category`    | string | Issue category             |
| `severity`    | string | Issue impact level         |
| `summary`     | string | Short summary of the issue |
| `next_action` | string | Recommended next step      |

## Allowed Categories

The API normalizes category values into one of the following:

```text
authentication
payment
performance
deployment
integration
general
```

## Allowed Severities

The API normalizes severity values into one of the following:

```text
low
medium
high
critical
```

## Reliability Features

LLM outputs can be unpredictable. To make the API more stable, this project includes several reliability-focused features.

### 1. JSON Parsing Guard

Gemini responses are parsed into JSON before being returned from the API.

If Gemini returns markdown-wrapped JSON, the service attempts to clean the response before parsing.

### 2. Response Normalization

The API normalizes category and severity values so that responses remain consistent.

For example:

```text
Payments → payment
Critical → critical
```

### 3. Fallback Response

If Gemini API fails or returns an invalid response, the API returns a safe fallback response instead of crashing.

Example fallback:

```json
{
  "category": "general",
  "severity": "low",
  "summary": "LLM triage failed. Returning fallback response.",
  "next_action": "Review the customer message manually."
}
```

### 4. Logging

The service uses Python logging to record failures and abnormal responses.

This helps identify issues such as:

* Gemini API call failure
* JSON parsing failure
* Unknown category values
* Unknown severity values

### 5. Schema-Level Validation

The response model uses Pydantic schema validation to enforce the API contract.

This prevents unexpected category or severity values from being returned by the API.

## Tech Stack

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* Gemini API
* python-dotenv
* Swagger UI
* Black
* isort
* Git / GitHub

## Project Structure

```text
app/
├── main.py
├── config.py
├── schemas/
│   └── triage.py
└── services/
    └── triage_service.py
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/blue-monkey0/llm-support-triage-api.git
cd llm-support-triage-api
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file in the project root.

```text
GEMINI_API_KEY=your_gemini_api_key
```

The `.env` file should not be committed to GitHub.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

### 6. Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

## Example Test Messages

You can test the API with the following messages in Swagger UI.

### Payment Issue

```json
{
  "message": "Payment is failing for all users after checkout"
}
```

### Authentication / SSO Issue

```json
{
  "message": "SSO integration with Okta stopped working after configuration update"
}
```

### Performance Issue

```json
{
  "message": "API latency increased after the latest deployment"
}
```

### Deployment Issue

```json
{
  "message": "Login API returns 500 after the latest deployment"
}
```

## Development Progress

### Day 1

* Set up Python 3.12
* Created virtual environment
* Initialized Git repository
* Connected GitHub remote repository
* Added basic project files

### Day 2

* Built FastAPI server
* Implemented GET and POST endpoints
* Added Pydantic request model
* Tested API using Swagger UI
* Implemented rule-based triage logic

### Day 3

* Refactored project structure into schemas and services
* Added `.env` configuration
* Integrated Gemini API
* Designed prompt for support triage
* Parsed LLM response into structured JSON
* Connected FastAPI endpoint with Gemini-based triage service

### Day 4

* Added logging
* Added fallback response handling
* Added JSON response cleanup
* Added category normalization
* Added severity normalization
* Strengthened response schema using Pydantic validation
* Improved API reliability for unstable LLM outputs

## Why This Project Matters

This project demonstrates how to convert an LLM use case into a backend API service.

It focuses on:

* API design
* Request and response validation
* External LLM integration
* Prompt engineering
* Structured output parsing
* Error handling
* Logging
* Fallback strategy
* Production-aware response design

These are important skills for Field Deployment Engineer, AI Product Engineer, and LLM application engineering roles.

## Next Steps

* Add unit tests with pytest
* Add Dockerfile
* Add API latency measurement
* Add request/response logging middleware
* Add CI with GitHub Actions
* Add deployment guide
* Add architecture diagram image
* Add demo GIF or short demo video
