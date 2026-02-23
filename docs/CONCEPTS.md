# GhostCommit – Concepts Glossary

This document explains every major technology and concept used in this project, in practical terms.

---

## FastAPI
Modern Python web framework built on Starlette and Pydantic.
Used to build the GhostCommit API.

Key benefits:
- Automatic OpenAPI docs
- Async support
- Built-in dependency injection

Used in:
- app/main.py
- app/api/

---

## Uvicorn
ASGI server used to run FastAPI applications.

Used in:
- Docker container entrypoint
- Local development server

---

## SQLAlchemy (2.0 ORM)
Python ORM used to define database models and interact with Postgres.

Key concepts:
- DeclarativeBase
- Mapped / mapped_column
- Relationship
- ForeignKey
- UniqueConstraint

Used in:
- app/models/
- app/db/session.py

---

## Alembic
Database migration tool for SQLAlchemy.

Purpose:
- Track schema changes as versioned scripts
- Apply incremental upgrades
- Allow rollback if needed

Important files:
- alembic/env.py
- alembic/versions/
- alembic.ini

---

## PostgreSQL
Relational database used to store:

- Tenants
- Repositories
- Pull Requests
- Rationale Summaries
- Audit Logs

Running via Docker Compose.

---

## Docker & Docker Compose
Used to create a reproducible development environment.

Services:
- api (FastAPI app)
- db (PostgreSQL)

Allows:
- One-command startup
- Consistent local environment
- CI parity

---

## Pydantic BaseSettings
Configuration management system.

Reads:
- .env file
- Environment variables

Automatically validates types.

Used in:
- app/core/config.py

---

## Structlog
Structured logging framework.

Benefits:
- JSON-compatible logs
- Context binding
- Easy integration with observability tools later

Used in:
- app/core/logging.py
- app/api/webhooks.py

---

## GitHub Webhooks
Mechanism for GitHub to notify external systems about events.

We verify:
- X-Hub-Signature-256
- X-GitHub-Event
- X-GitHub-Delivery

Security:
- HMAC SHA256 verification
- Constant-time signature comparison

Used in:
- app/api/webhooks.py
- app/utils/github_sig.py

---

## HMAC Signature Verification
Security mechanism for verifying webhook authenticity.

Process:
1. GitHub signs payload with secret
2. We compute HMAC SHA256 with same secret
3. Compare signatures using constant-time comparison

Ensures:
- Request integrity
- Source authenticity

---

## Multi-Tenant Design
All core tables include:

- tenant_id

This allows:
- Future SaaS model
- Isolation between customers
- Horizontal scaling

---

## Unique Constraints
Ensures data correctness.

Examples:
- One repo per tenant (owner + name)
- One PR number per repo

Implemented via:
- SQLAlchemy UniqueConstraint
- Alembic migrations

---

## CI (GitHub Actions)
Automated quality enforcement.

Runs:
- Ruff (linting)
- MyPy (type checking)
- Pytest (unit tests)

Prevents broken code from reaching main.

Workflow file:
- .github/workflows/ci.yml