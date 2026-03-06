from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMMessage:
    role: str  # "system" | "user"
    content: str


class LLMClient(Protocol):
    def generate(self, *, messages: list[LLMMessage], temperature: float = 0.2) -> str:
        ...
