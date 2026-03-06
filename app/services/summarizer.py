from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pull_request import PullRequest
from app.models.rationale_summary import RationaleSummary
from app.services.llm.base import LLMClient, LLMMessage
from app.utils.pii import redact_json


@dataclass(frozen=True)
class SummarizeResult:
    stored: bool
    pr_id: int
    summary_id: int | None
    content: str  # the raw JSON string produced by the LLM


class SummarizerService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def generate_for_pr(self, db: Session, *, pr_id: int) -> SummarizeResult:
        pr = db.get(PullRequest, pr_id)
        if not pr:
            raise ValueError(f"PullRequest {pr_id} not found")

        payload_obj = _safe_json_loads(pr.raw_payload) if pr.raw_payload else {}
        redacted_payload, counts = (
            redact_json(payload_obj) if settings.pii_redaction_enabled else (payload_obj, {})
        )

        prompt = _build_prompt(
            repo_owner=_payload_repo_owner(payload_obj) or "",
            repo_name=_payload_repo_name(payload_obj) or "",
            pr_number=pr.pr_number,
            title=pr.title,
            author=pr.author,
            redacted_payload=redacted_payload,
            pii_counts=counts,
        )

        content = self._llm.generate(
            messages=[
                LLMMessage(role="system", content=_SYSTEM_INSTRUCTIONS),
                LLMMessage(role="user", content=prompt),
            ],
            temperature=0.2,
        )

        parsed = _safe_json_loads_any(content)
        risk_level = _get_str(parsed, "risk_level") or "medium"

        # Normalize to allowed values
        if risk_level not in {"low", "medium", "high"}:
            risk_level = "medium"

        row = RationaleSummary(
            tenant_id=pr.tenant_id,
            repo_id=pr.repo_id,
            pr_id=pr.id,
            summary_json=content,
            risk_level=risk_level,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        return SummarizeResult(stored=True, pr_id=pr.id, summary_id=row.id, content=content)


_SYSTEM_INSTRUCTIONS = """You generate a structured "Decision Rationale" for a pull request.
Return STRICT JSON with keys:
- summary (string)
- decision (string)
- why (string)
- alternatives (array of strings)
- risks (array of strings)
- rollout (array of strings)
- risk_level (string: one of "low", "medium", "high")
- metadata (object)
Do NOT include secrets or PII.
"""


def _get_str(d: dict[str, Any], key: str) -> str | None:
    v = d.get(key)
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return str(v)


def _build_prompt(
    *,
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    title: str,
    author: str,
    redacted_payload: dict[str, Any],
    pii_counts: dict[str, int],
) -> str:
    return "\n".join(
        [
            f"REPO: {repo_owner}/{repo_name}".strip("/"),
            f"PR_NUMBER: {pr_number}",
            f"TITLE: {title}",
            f"AUTHOR: {author}",
            f"PII_REDACTION_COUNTS: {json.dumps(pii_counts, ensure_ascii=False)}",
            "PAYLOAD_JSON:",
            json.dumps(redacted_payload, ensure_ascii=False),
        ]
    )


def _safe_json_loads(s: str) -> dict[str, Any]:
    """Loads JSON, returns dict if it's a dict, else {}."""
    try:
        v = json.loads(s)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def _safe_json_loads_any(s: str) -> dict[str, Any]:
    """
    Loads JSON where the input might be an LLM output string.
    Ensures a dict[str, Any] for mypy (no Any-return leakage).
    """
    return _safe_json_loads(s)


def _payload_repo_owner(payload: dict[str, Any]) -> str | None:
    repo = payload.get("repository")
    if not isinstance(repo, dict):
        return None
    owner = repo.get("owner")
    if not isinstance(owner, dict):
        return None
    login = owner.get("login")
    return login if isinstance(login, str) else None


def _payload_repo_name(payload: dict[str, Any]) -> str | None:
    repo = payload.get("repository")
    if not isinstance(repo, dict):
        return None
    name = repo.get("name")
    return name if isinstance(name, str) else None