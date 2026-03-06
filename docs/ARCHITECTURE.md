1. System Overview

GhostCommit is a contextual intelligence engine for pull requests.

It:

Receives GitHub webhook events

Stores PR metadata + raw payload

Redacts PII before AI processing

Generates structured decision rationale summaries

Persists summaries with risk classification

Exposes retrieval via a context API

The architecture is layered for clarity and testability.


2. High-Level Architecture

           GitHub
              │
              ▼
     POST /webhooks/github
              │
      Signature Verification
              │
              ▼
        pull_requests table
              │
              ▼
 POST /summaries/generate?pr_id=…
              │
        PII Redaction Layer
              │
              ▼
          LLM Client
              │
              ▼
   rationale_summaries table
              │
              ▼
     GET /context?owner=...&repo=...&pr=...



3. Runtime Architecture
API Layer

FastAPI application

Routes organized by domain:

health

webhooks

summaries

context

Service Layer

SummarizerService

LLM abstraction (LLMClient)

DeterministicLLM for testing

Safety Layer

app/utils/pii.py

Redacts:

Emails

Phone numbers

GitHub tokens

AWS keys

Private keys

Controlled via config flags

Persistence Layer

SQLAlchemy 2.0 ORM

PostgreSQL via Docker

Alembic for migrations


4. Database Schema
tenants

Supports multi-tenant architecture.

Fields:

id (PK)

name

repos

Represents a source repository.

Fields:

id (PK)

tenant_id (FK)

provider

owner

name

Constraint:

Unique per (tenant_id, owner, name)


pull_requests

Stores PR metadata and raw webhook payload.

Fields:

id (PK)

tenant_id (FK)

repo_id (FK)

pr_number

title

author

state

raw_payload (JSON string)

Constraint:

Unique per (repo_id, pr_number)

rationale_summaries

Stores AI-generated structured decision rationale.

Fields:

id (PK)

tenant_id (FK)

repo_id (FK)

pr_id (FK)

summary_json (text, structured JSON from LLM)

risk_level (low | medium | high)

created_at (timestamp)

Important:

summary_json stores the full LLM JSON output.

API layer extracts human-readable content from it.


5. Security Model
Webhook Security

HMAC SHA256 verification

Constant-time comparison

Rejects invalid signatures with 401

Headers validated:

X-Hub-Signature-256

X-GitHub-Event

X-GitHub-Delivery

PII Protection

Before sending data to LLM:

Webhook payload is recursively redacted

Regex-based detection of sensitive patterns

Configurable via:

pii_redaction_enabled

pii_redaction_mode

This prevents secrets from leaking into AI prompts.


6. API Contract
Health
GET /health
GET /ready
POST /webhooks/github

Summary Generation
POST /summaries/generate?pr_id=INTEGER

Generates structured JSON summary

Extracts risk_level

Persists to database

Returns:
{
status,
pr_id,
summary_id
}

Note:

pr_id is a query parameter (not JSON body).

Context Retrieval
GET /context?owner=...&repo=...&pr=...

Returns:

repo metadata

pull_request metadata

latest rationale_summary (if exists)

Optional:

include_raw=true

to return raw webhook payload.


7. Testing Architecture

Tests use:

SQLite in-memory database

StaticPool to preserve connection

FastAPI dependency override for get_db

DeterministicLLM for predictable outputs

Ensures:

No external services required

Fully deterministic CI

Zero network dependency

8. Deployment Model

Current:

Docker Compose (API + Postgres)

Future-Ready For:

Kubernetes

Horizontal scaling

Background job workers

Real LLM provider integration

9. Architectural Principles

Type safety enforced (MyPy clean)

Linting enforced (Ruff clean)

Strict CI gate

Multi-tenant by default

No PII exposure to LLM

Structured JSON outputs

Clear separation of API, service, and persistence layers

10. Current Maturity Level

GhostCommit is currently:

Architecturally stable

Test-covered

CI-enforced

Production-structured (but still synchronous)

Deterministic LLM (for safety)

Next recommended evolution:

Versioned summaries

Real LLM provider

Async background processingcon 