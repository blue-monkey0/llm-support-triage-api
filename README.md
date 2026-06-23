# LLM Support Triage API

LLM Support Triage API is a FastAPI-based backend project that classifies customer support messages into issue categories and severity levels.

This project is designed as a practical FDE-oriented backend system. Instead of building a simple chatbot, it focuses on the first step of real customer support workflows: understanding the issue, classifying it, estimating severity, and suggesting the next action.

## Problem

Support engineers often receive customer issues such as:

* Login failures
* Payment failures
* Slow API responses
* Deployment-related errors
* Integration issues

Before solving the issue, engineers need to quickly answer:

1. What type of issue is this?
2. How severe is it?
3. What should be checked first?
4. Which team should handle it?

This process is called support triage.

## Current Features

* FastAPI server setup
* Health/root endpoint
* POST `/triage` endpoint
* Pydantic request validation
* Swagger UI API testing
* Rule-based support ticket classification

## API Example

### Request

```json
{
  "message": "Login API returns 500 after deployment"
}
```

### Response

```json
{
  "category": "authentication",
  "severity": "high",
  "summary": "Login-related issue detected.",
  "next_action": "Check authentication service logs and recent deployments."
}
```

## Current Triage Logic

| Keyword       | Category       | Severity |
| ------------- | -------------- | -------- |
| login         | authentication | high     |
| payment       | payment        | high     |
| slow, latency | performance    | medium   |
| others        | general        | low      |

## Tech Stack

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* Swagger UI
* Git / GitHub

## Project Roadmap

### Week 1

* Build FastAPI server
* Implement rule-based triage endpoint
* Add request validation with Pydantic
* Document API behavior
* Prepare Docker execution environment

### Next Steps

* Integrate OpenAI API for LLM-based classification
* Add structured response schema
* Add error handling
* Add latency measurement
* Add logging
* Add tests with pytest
* Add Dockerfile

## How to Run

```bash
cd ~/Desktop/fde-week1
source .venv/bin/activate
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Why This Project Matters

This project demonstrates the ability to convert an AI use case into a backend API service. It focuses on API design, request validation, structured responses, and customer-support-oriented workflow automation, which are important skills for Field Deployment Engineer and AI application engineering roles.
