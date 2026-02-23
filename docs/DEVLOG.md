# GhostCommit – Development Log

This file documents major technical decisions and progress milestones.

---

## 2026-02-23 — Phase 1 Complete

### What Was Done
- Initialized repository structure
- Created Docker Compose stack (API + Postgres)
- Implemented health and readiness endpoints
- Configured Pydantic BaseSettings for .env config
- Added structlog structured logging
- Set up Ruff, MyPy, Pytest
- Fixed ruff import sorting issues
- Added default database_url to satisfy MyPy
- Aligned CI to use `python -m` execution
- Confirmed CI green

### Why These Decisions

**Docker First Approach**
Ensures environment parity between local and CI.

**Strict Lint + Type Enforcement Early**
Prevents technical debt accumulation.

**Structured Logging From Day 1**
Allows future observability expansion without refactor.

---

## 2026-02-23 — Phase 2 Schema Design

### What Was Done
- Designed core relational schema:
  - tenants
  - repos
  - pull_requests
  - rationale_summaries
  - audit_logs
- Implemented SQLAlchemy models
- Generated Alembic migrations
- Added uniqueness constraints:
  - repo uniqueness per tenant
  - PR uniqueness per repo
- Created seed script for local testing

### Why This Design

**Multi-Tenant From Start**
Even though solo MVP, architecture anticipates SaaS.

**Store Raw Payload**
Allows:
- Reprocessing
- Re-summarization
- Debugging webhook issues

**Explicit Unique Constraints**
Guarantees data correctness at DB level, not just application layer.

---

## 2026-02-23 — Webhook Signature Verification (Issue #6)

### What Was Done
- Implemented HMAC SHA256 verification
- Validated X-Hub-Signature-256
- Enforced 401 on invalid signatures
- Verified using local OpenSSL signature generation

### Lessons Learned
- Structlog reserves `event` keyword
- Always use `python -m` in CI
- Curl can mutate request body unless using --data-binary

---

## Next Milestone
Issue #7 — PR ingestion:

- Parse pull_request event
- Upsert PR metadata
- Detect merge event
- Store raw payload