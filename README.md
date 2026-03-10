# AI DevOps Copilot

AI DevOps Copilot is an AI-powered log analysis system designed to help engineers quickly diagnose issues in cloud and containerized environments.

The system ingests application logs and uses Large Language Models (LLMs) to automatically perform root cause analysis and suggest fixes.

This project demonstrates concepts used in:

- Cloud Reliability Engineering (CRE)
- Site Reliability Engineering (SRE)
- AIOps (AI for IT Operations)
- DevOps automation

---

## Architecture

Application Logs
        ↓
FastAPI Log Ingestion API
        ↓
AI Analysis (OpenAI API)
        ↓
Root Cause + Suggested Fix

The system runs in a containerized environment using Docker.

---

## Features

- Upload logs via API
- AI-powered root cause analysis
- Suggested remediation steps
- Containerized deployment with Docker
- FastAPI backend
- PostgreSQL support (via Docker Compose)

---

## Example Workflow

Generate an application error:

GET /error

Upload logs for AI analysis:

curl -X POST http://localhost:8000/upload-log \
-F "file=@logs/app.log"

Issue:
Division by zero error detected

Root Cause:
Application attempted division without validating denominator

Suggested Fix:
Add validation before division.

Severity:
High
