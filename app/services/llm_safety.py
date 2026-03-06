import json
from typing import Any

import structlog

from app.core.config import settings
from app.utils.pii import redact_json, redact_text

log = structlog.get_logger()


def prepare_llm_input_text(text: str) -> str:
    if not settings.pii_redaction_enabled:
        return text

    res = redact_text(text)
    if res.counts:
        log.info("pii_redaction_applied", **res.counts)
    return res.text


def prepare_llm_input_json(payload: Any) -> str:
    """
    Returns a JSON string safe to send to LLMs.
    """
    if not settings.pii_redaction_enabled:
        return json.dumps(payload)

    redacted, counts = redact_json(payload)
    if counts:
        log.info("pii_redaction_applied", **counts)
    return json.dumps(redacted)