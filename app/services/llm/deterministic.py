from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from app.services.llm.base import LLMClient, LLMMessage


class DeterministicLLM(LLMClient):
    """
    Deterministic placeholder. Produces a structured rationale without external calls.
    This lets you ship, test, and demo safely.
    """

    def generate(self, *, messages: list[LLMMessage], temperature: float = 0.2) -> str:
        # Expect the last message to carry the payload/context
        user = next((m for m in reversed(messages) if m.role == "user"), None)
        text = user.content if user else ""

        # Very lightweight heuristics:
        title = _extract_line(text, "TITLE:")
        author = _extract_line(text, "AUTHOR:")
        repo = _extract_line(text, "REPO:")
        pr_number = _extract_line(text, "PR_NUMBER:")

        out: dict[str, Any] = {
            "summary": f"PR #{pr_number} in {repo}: {title}".strip(),
            "decision": "Implement changes described by the PR.",
            "why": "Captured from PR metadata; detailed rationale requires PR body + linked discussions.",
            "alternatives": ["Do nothing", "Implement a smaller incremental change"],
            "risks": ["Hidden coupling", "Incomplete context if discussions live outside GitHub"],
            "rollout": ["Merge to main", "Monitor errors/logs", "Rollback if necessary"],
            "risk_level": "low",
            "metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "author": author,
            },
        }
        return json.dumps(out, ensure_ascii=False)


def _extract_line(blob: str, prefix: str) -> str:
    for line in blob.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""