from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RedactionResult:
    text: str
    counts: dict[str, int]


_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_IPv4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b")

# Phone heuristic: supports formats like:
# +1 913-207-1660, (913) 207 1660, 9132071660, +44 20 1234 5678
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}(?!\d)"
)

# GitHub tokens
_GH_TOKEN_RE = re.compile(r"\b(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")

# AWS key ids
_AWS_KEY_ID_RE = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")

# Private key blocks
_PRIVATE_KEY_BLOCK_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----",
    re.MULTILINE,
)

# Generic secret assignment patterns
_GENERIC_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|password|passwd|pwd|token|bearer)\b\s*[:=]\s*([^\s'\";]+)"
)


def redact_text(text: str) -> RedactionResult:
    """
    Redact likely PII and secret material from a text blob.
    Deterministic regex-based sanitizer for MVP.
    """
    counts: dict[str, int] = {}

    def sub(pattern: re.Pattern[str], replacement: str, label: str, s: str) -> str:
        new_s, n = pattern.subn(replacement, s)
        if n:
            counts[label] = counts.get(label, 0) + n
        return new_s

    s = text

    # Secrets first (more sensitive)
    s = sub(_PRIVATE_KEY_BLOCK_RE, "[REDACTED_PRIVATE_KEY]", "private_key_block", s)
    s = sub(_GH_TOKEN_RE, "[REDACTED_TOKEN]", "github_token", s)
    s = sub(_AWS_KEY_ID_RE, "[REDACTED_AWS_KEY_ID]", "aws_key_id", s)

    # Generic secret assignments
    def repl_generic(m: re.Match[str]) -> str:
        key = m.group(1)
        counts["generic_secret"] = counts.get("generic_secret", 0) + 1
        return f"{key}=[REDACTED_SECRET]"

    s = _GENERIC_SECRET_RE.sub(repl_generic, s)

    # PII
    s = sub(_EMAIL_RE, "[REDACTED_EMAIL]", "email", s)
    s = sub(_PHONE_RE, "[REDACTED_PHONE]", "phone", s)
    s = sub(_IPv4_RE, "[REDACTED_IP]", "ipv4", s)

    return RedactionResult(text=s, counts=counts)


def redact_json(obj: Any) -> tuple[Any, dict[str, int]]:
    """
    Recursively redact strings within a JSON-like structure (dict/list/str).
    Returns (redacted_obj, counts).
    """
    counts: dict[str, int] = {}

    def merge(c: dict[str, int]) -> None:
        for k, v in c.items():
            counts[k] = counts.get(k, 0) + v

    if isinstance(obj, str):
        res = redact_text(obj)
        merge(res.counts)
        return res.text, counts

    if isinstance(obj, list):
        out_list = []
        for item in obj:
            red, c = redact_json(item)
            merge(c)
            out_list.append(red)
        return out_list, counts

    if isinstance(obj, dict):
        out_dict: dict[str, Any] = {}
        for k, v in obj.items():
            red, c = redact_json(v)
            merge(c)
            out_dict[k] = red
        return out_dict, counts

    # numbers, bools, None
    return obj, counts