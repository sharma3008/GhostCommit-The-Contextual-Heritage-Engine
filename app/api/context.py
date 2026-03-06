from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.pull_request import PullRequest
from app.models.rationale_summary import RationaleSummary
from app.models.repo import Repo
from app.schemas.context import ContextOut, PullRequestOut, RationaleSummaryOut, RepoOut

router = APIRouter(tags=["context"])


def _extract_summary_text(summary_json: str) -> str:
    """
    Our DB stores the summary as JSON text in rationale_summaries.summary_json.
    We expose a clean 'content' string on the API.
    """
    try:
        obj = json.loads(summary_json)
        if isinstance(obj, dict):
            # Prefer common keys, fall back to first string-ish value
            for k in ("decision_rationale", "content", "summary", "rationale", "text"):
                v = obj.get(k)
                if isinstance(v, str) and v.strip():
                    return v
            return json.dumps(obj, ensure_ascii=False)
        # If it's a list/primitive, stringify
        return json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
    except Exception:
        # If it's not valid JSON, just return as-is
        return summary_json


@router.get("/context", response_model=ContextOut)
def get_context(
    owner: str = Query(..., min_length=1),
    repo: str = Query(..., min_length=1),
    pr: int = Query(..., ge=1),
    include_raw: bool = Query(False),
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> ContextOut:
    repo_row = db.scalar(select(Repo).where(Repo.owner == owner, Repo.name == repo))
    if not repo_row:
        raise HTTPException(status_code=404, detail="Repo not found")

    pr_row = db.scalar(
        select(PullRequest).where(
            PullRequest.repo_id == repo_row.id,
            PullRequest.pr_number == pr,
        )
    )
    if not pr_row:
        raise HTTPException(status_code=404, detail="Pull request not found")

    summary_row = db.scalar(
        select(RationaleSummary)
        .where(RationaleSummary.pr_id == pr_row.id)
        .order_by(RationaleSummary.id.desc())
        .limit(1)
    )

    repo_out = RepoOut(
        id=repo_row.id,
        tenant_id=repo_row.tenant_id,
        provider=getattr(repo_row, "provider", "github"),
        owner=repo_row.owner,
        name=repo_row.name,
    )

    pr_out = PullRequestOut(
        id=pr_row.id,
        repo_id=pr_row.repo_id,
        tenant_id=pr_row.tenant_id,
        pr_number=pr_row.pr_number,
        title=pr_row.title,
        author=pr_row.author,
        state=pr_row.state,
        merged_at=getattr(pr_row, "merged_at", None),
        raw_payload=pr_row.raw_payload if include_raw else None,
    )

    summary_out: RationaleSummaryOut | None = None
    if summary_row is not None:
        summary_json = getattr(summary_row, "summary_json", "")
        content_str = _extract_summary_text(summary_json) if summary_json else ""

        summary_out = RationaleSummaryOut(
            id=summary_row.id,
            pr_id=summary_row.pr_id,
            repo_id=summary_row.repo_id,
            tenant_id=summary_row.tenant_id,
            content=content_str,
            created_at=getattr(summary_row, "created_at", None),
        )

    return ContextOut(repo=repo_out, pull_request=pr_out, rationale_summary=summary_out)