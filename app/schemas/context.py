from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class RepoOut(BaseModel):
    id: int
    tenant_id: int
    provider: str
    owner: str
    name: str


class PullRequestOut(BaseModel):
    id: int
    repo_id: int
    tenant_id: int
    pr_number: int
    title: str
    author: str
    state: str
    merged_at: datetime | None = None
    raw_payload: Any | None = None  # only returned when include_raw=true


class RationaleSummaryOut(BaseModel):
    id: int
    pr_id: int
    repo_id: int
    tenant_id: int
    content: str
    created_at: datetime | None = None


class ContextOut(BaseModel):
    repo: RepoOut
    pull_request: PullRequestOut
    rationale_summary: RationaleSummaryOut | None = None
