"""Append-only per-source store with deduplication.

Files:
  data/<source>.txt     — human-readable, one block per item
  data/<source>.jsonl   — JSONL, used to rebuild XLSX snapshots
  data/<source>.seen    — newline-delimited stable IDs already saved
                          (tracked separately so the JSONL stays clean append-only)

We never load full datasets into RAM. The seen-set is loaded once at startup
into memory (only IDs, ~tens of bytes each) for O(1) duplicate checks during
the run.
"""
from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from app.core.logger import get_logger

log = get_logger("store")


def _fmt_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    return json.dumps(v, ensure_ascii=False)


@dataclass
class SourceStore:
    """Append-only writer for a single source."""

    source: str
    columns: List[str]
    data_dir: Path
    seen: Set[str] = field(default_factory=set)
    total_seen: int = 0
    new_added: int = 0
    last_added_at: Optional[float] = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.txt_path.touch(exist_ok=True)
        self.jsonl_path.touch(exist_ok=True)
        if self.seen_path.exists():
            with self.seen_path.open("r", encoding="utf-8") as f:
                for line in f:
                    sid = line.strip()
                    if sid:
                        self.seen.add(sid)
            self.total_seen = len(self.seen)

    @property
    def txt_path(self) -> Path:
        return self.data_dir / f"{self.source}.txt"

    @property
    def jsonl_path(self) -> Path:
        return self.data_dir / f"{self.source}.jsonl"

    @property
    def seen_path(self) -> Path:
        return self.data_dir / f"{self.source}.seen"

    def add(self, item_id: str, row: Dict[str, Any]) -> bool:
        """Add a row if id is unseen. Returns True if appended."""
        if not item_id:
            return False
        with self._lock:
            if item_id in self.seen:
                return False
            self.seen.add(item_id)
            self.total_seen += 1
            self.new_added += 1
            import time
            self.last_added_at = time.time()
            with self.txt_path.open("a", encoding="utf-8") as f:
                for col in self.columns:
                    f.write(f"{col}: {_fmt_value(row.get(col))}\n")
                f.write("-" * 60 + "\n")
            with self.jsonl_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            with self.seen_path.open("a", encoding="utf-8") as f:
                f.write(item_id + "\n")
            return True

    def reset(self) -> None:
        with self._lock:
            self.seen.clear()
            self.total_seen = 0
            self.new_added = 0
            self.last_added_at = None
            for p in (self.txt_path, self.jsonl_path, self.seen_path):
                p.write_text("", encoding="utf-8")


class Store:
    """Container for all per-source stores."""

    def __init__(self, data_dir: Path, sources: Dict[str, List[str]]) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sources: Dict[str, SourceStore] = {
            src: SourceStore(source=src, columns=cols, data_dir=data_dir)
            for src, cols in sources.items()
        }
        self._lock = asyncio.Lock()

    def get(self, source: str) -> SourceStore:
        return self.sources[source]

    def stats(self) -> Dict[str, Dict[str, Any]]:
        return {
            s: {
                "total": store.total_seen,
                "new_session": store.new_added,
                "last_added_at": store.last_added_at,
            }
            for s, store in self.sources.items()
        }

    def total(self) -> int:
        return sum(s.total_seen for s in self.sources.values())

    def reset_all(self) -> None:
        for s in self.sources.values():
            s.reset()

    def reset_one(self, source: str) -> None:
        if source in self.sources:
            self.sources[source].reset()

    def iter_sources(self) -> Iterable[str]:
        return self.sources.keys()
