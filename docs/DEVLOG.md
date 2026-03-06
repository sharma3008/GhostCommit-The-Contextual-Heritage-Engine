# GhostCommit – Development Log

Chronological record of major engineering decisions and milestones.

---

## 2026-02-23 — Phase 1 Foundations

### Completed
- Initialized repository structure
- Docker Compose stack (API + Postgres)
- Health and readiness endpoints
- BaseSettings configuration
- Structured logging with Structlog
- Ruff + MyPy + Pytest setup
- CI pipeline configured
- Confirmed CI green

### Key Decisions

**Strict lint + type enforcement early**
Prevents long-term technical debt.

**Docker-first workflow**
Ensures environment consistency across dev and CI.

---

## 2026-02-23 — Phase 2 Schema Design

### Completed
- Designed relational schema:
  - tenants
  - repos
  - pull_requests
  - rationale_summaries
  - audit_logs
- Added unique constraints:
  - Repo uniqueness per tenant
  - PR uniqueness per repo
- Generated Alembic migrations
- Created seed script

### Design Rationale

**Multi-tenant from start**
Prepares system for SaaS model.

**Store raw webhook payload**
Allows:
- Reprocessing
- Debugging
- Re-summarization

---

## 2026-02-23 — Webhook Signature Verification (Issue #6)

### Completed
- Implemented HMAC SHA256 verification
- Enforced 401 on invalid signature
- Verified using OpenSSL locally

### Lessons
- Structlog reserves `event` keyword
- Always use `--data-binary` with curl for exact payload
- CI must use `python -m`

---

## 2026-02-23 — PR Ingestion (Issue #7)

### Completed
- Parse pull_request webhook event
- Upsert PR metadata
- Store raw payload
- Handle merged/open state transitions

---

## 2026-02-23 — PII Redaction Layer (Issue #8)

### Completed
- Implemented deterministic regex redaction
- Added recursive JSON support
- Added unit tests
- Config toggle for enabling/disabling redaction

### Why

Protect secrets from leaking into LLM prompts.

---

## 2026-02-24 — Summary Generation Engine (Issue #9)

### Completed
- Introduced LLM abstraction layer
- Implemented DeterministicLLM
- Created SummarizerService
- Enforced structured JSON output
- Extracted and normalized risk_level
- Persisted summary_json + risk_level
- Added /summaries/generate endpoint
- Added /context retrieval endpoint
- Added SQLite StaticPool test harness
- Fixed FastAPI dependency injection edge cases
- Achieved full Ruff + MyPy + Pytest clean state

### Architectural Decisions

**Store entire LLM output as JSON text**
- Allows re-parsing later
- Enables schema evolution
- Avoids premature flattening

**Synchronous generation (for now)**
- Simpler architecture
- Easier debugging
- Background jobs planned later

---

## Current Status

System is:

- Fully type-safe
- CI-enforced
- Deterministic and testable
- Multi-tenant ready
- PII-safe before LLM invocation
- Structured AI output stored and retrievable

Next planned milestone:
- Versioned summaries (Issue #10)
- Real LLM provider integration
- Background job processing