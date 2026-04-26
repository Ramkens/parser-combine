"""Base classes for source parsers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

from app.core.http import HttpClient


@dataclass
class ParseTask:
    """Per-run input passed to every parser."""

    keywords: List[str]
    limit: int = 100  # max items per parser
    extra: Optional[Dict[str, Any]] = None  # source-specific overrides

    def opt(self, key: str, default: Any = None) -> Any:
        if self.extra is None:
            return default
        return self.extra.get(key, default)


class BaseParser(ABC):
    """All parsers implement an async generator that yields dict rows."""

    name: str = "base"
    columns: List[str] = ["title", "url"]

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    @abstractmethod
    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        """Yield row dicts. Must be an async generator."""
        raise NotImplementedError
