# GhostCommit – Concepts Glossary

This document explains every major technology and architectural concept used in GhostCommit.

---

## FastAPI

Modern Python web framework built on Starlette and Pydantic.

Key benefits:
- Automatic OpenAPI documentation
- Built-in dependency injection
- Async support
- Strong type integration

Used in:
- app/main.py
- app/api/

---

## Uvicorn

ASGI server used to run the FastAPI application.

Used in:
- Docker container entrypoint
- Local development server

---

## SQLAlchemy (2.0 ORM)

Python ORM used to define models and interact with PostgreSQL.

Key concepts:
- Declarative Base
- `Mapped` / `mapped_column`
- `ForeignKey`
- `UniqueConstraint`
- `select()` query style (2.0 syntax)

Used in:
- app/models/
- app/db/

---

## Alembic

Database migration tool for SQLAlchemy.

Purpose:
- Track schema changes as versioned scripts
- Upgrade database safely
- Maintain production-safe schema evolution

Used in:
- alembic/env.py
- alembic/versions/

---

## PostgreSQL

Primary relational database.

Stores:
- Tenants
- Repositories
- Pull Requests
- Rationale Summaries
- Audit Logs

Runs inside Docker for development.

---

## Docker & Docker Compose

Used to create reproducible environments.

Services:
- api (FastAPI app)
- db (Postgres)

Benefits:
- Environment parity
- One-command startup
- CI consistency

---

## Pydantic BaseSettings

Configuration system using environment variables.

Reads:
- .env file
- Environment variables

Validates:
- Types
- Defaults
- Required settings

Used in:
- app/core/config.py

---

## Structlog

Structured logging framework.

Benefits:
- JSON-compatible logs
- Context binding
- Production-ready logging format

Used in:
- app/core/logging.py
- app/api/webhooks.py

Note:
Avoid using reserved key `event` in logs.

---

## GitHub Webhooks

GitHub sends POST requests when events occur.

We validate:
- X-Hub-Signature-256
- X-GitHub-Event
- X-GitHub-Delivery

Used in:
- app/api/webhooks.py
- app/utils/github_sig.py

---

## HMAC Signature Verification

Security mechanism for verifying webhook authenticity.

Process:
1. GitHub signs payload using shared secret
2. Server computes HMAC SHA256 with same secret
3. Compare signatures using constant-time comparison

Prevents:
- Tampered payloads
- Forged webhook calls

---

## Multi-Tenant Architecture

All core tables include:
- tenant_id

Allows:
- SaaS future model
- Data isolation
- Customer separation

---

## Unique Constraints

Ensures database-level correctness.

Examples:
- One repo per tenant (owner + name)
- One PR number per repo

Defined via:
- SQLAlchemy constraints
- Alembic migrations

---

## PII Redaction

Regex-based sanitization layer to remove likely personal data and secrets before sending content to LLM.

Detects:
- Emails
- Phone numbers
- GitHub tokens
- AWS keys
- Private key blocks

Supports:
- Recursive JSON redaction
- Config toggle via settings

Used in:
- app/utils/pii.py
- app/services/summarizer.py

---

## LLM Abstraction Layer

Abstract interface for AI providers.

Components:
- LLMClient (base interface)
- DeterministicLLM (test implementation)

Purpose:
- Testability
- Future OpenAI/Anthropic integration
- Clean service-layer isolation

Used in:
- app/services/llm/
- app/services/summarizer.py

---

## Structured AI Output

LLM returns strict JSON with fields:

- summary
- decision
- why
- alternatives
- risks
- rollout
- risk_level
- metadata

Stored as:
- summary_json (text column)

Allows:
- Structured parsing
- Future reprocessing
- Risk scoring

---

## Context Retrieval Endpoint

GET /context

Returns:
- repo metadata
- pull request metadata
- latest AI rationale summary

Optional:
- include_raw=true to return raw webhook payload

Used in:
- app/api/context.py
- app/schemas/context.py

---

## SQLite StaticPool (Testing)

Used in tests to:
- Share a single in-memory SQLite connection
- Prevent "no such table" issues across requests

Used in:
- tests/test_context.py

---

## FastAPI Dependency Overrides (Testing)

Allows replacing production DB session with in-memory SQLite session during tests.

Used in:
- tests/