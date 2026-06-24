# LLM Support Triage API

LLM Support Triage API is a FastAPI-based backend project that classifies customer support messages using a Large Language Model.

This project is designed as a practical FDE-oriented AI backend system. Instead of building a simple chatbot, it focuses on the first step of real customer support workflows: understanding the issue, classifying it, estimating severity, and suggesting the next action.

## Problem

Support engineers often receive customer issues such as:

* Login failures
* Payment failures
* Slow API responses
* Deployment-related errors
* Third-party integration issues

Before solving the issue, engineers need to quickly answer:

1. What type of issue is this?
2. How severe is it?
3. What should be checked first?
4. Which team should handle it?

This process is called support triage.

## Current Features

* FastAPI server setup
* POST `/triage` endpoint
* Pydantic request/response validation
* Swagger UI API testing
* Gemini API integration
* LLM-based support ticket classification
* Structured JSON response generation
* Basic fallback response when LLM triage fails
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
  "summary": "All payment transactions are failing for users after checkout.",
  "next_action": "Escalate to the on-call engineering team and investigate payment gateway logs."
}
```

## Response Fields

| Field         | Description                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------ |
| `category`    | Issue category such as authentication, payment, performance, deployment, integration, or general |
| `severity`    | Impact level: low, medium, high, or critical                                                     |
| `summary`     | Short summary of the customer issue                                                              |
| `next_action` | Recommended next step for support or engineering teams                                           |

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

```bash
cd ~/Desktop/fde-week1
source .venv/bin/activate
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

Create a `.env` file in the project root.

```text
GEMINI_API_KEY=your_gemini_api_key
```

`.env` should not be committed to GitHub.

## Development Progress

### Day 1

* Set up Python 3.12
* Created virtual environment
* Initialized Git repository
* Connected GitHub remote repository

### Day 2

* Built FastAPI server
* Implemented GET and POST endpoints
* Added Pydantic request validation
* Tested API using Swagger UI
* Implemented rule-based triage logic

### Day 3

* Refactored project structure into schemas and services
* Added `.env` configuration
* Integrated Gemini API
* Designed prompt for support triage
* Parsed LLM response into structured JSON
* Added basic fallback handling

## Next Steps

* Improve exception handling
* Add logging
* Add response normalization
* Add latency measurement
* Add pytest tests
* Add Dockerfile
* Add deployment guide

## Why This Project Matters

This project demonstrates the ability to convert an AI use case into a backend API service. It focuses on API design, request validation, external LLM integration, structured responses, and customer-support-oriented workflow automation, which are important skills for Field Deployment Engineer and AI application engineering roles.
