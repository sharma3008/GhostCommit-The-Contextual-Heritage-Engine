from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.services.llm.deterministic import DeterministicLLM
from app.services.summarizer import SummarizerService

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/generate")
def generate_summary(
    pr_id: int = Query(..., ge=1),
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> dict:
    llm = DeterministicLLM()
    service = SummarizerService(llm=llm)
    try:
        result = service.generate_for_pr(db, pr_id=pr_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {exc}") from exc

    return {
        "stored": result.stored,
        "pr_id": result.pr_id,
        "summary_id": result.summary_id,
        "content": result.content,
    }