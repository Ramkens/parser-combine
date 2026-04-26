"""Base classes for harvester sources."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Tuple

from app.core.http import HttpClient


class BaseSource(ABC):
    """A source emits (item_id, row_dict) pairs.

    item_id must be stable across runs (e.g. AppID for Steam, AssetID for
    Roblox) so dedup works correctly. Each call to `tick()` performs one
    sweep over the source — the harvester invokes `tick` repeatedly with
    the configured interval.
    """

    name: str = "base"
    columns: List[str] = ["title", "url"]
    interval: float = 600.0  # seconds between successive ticks for this source
    display: str = ""
    category: str = "misc"

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    @abstractmethod
    def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        """Async-generate (id, row) pairs for one sweep."""
        raise NotImplementedError
