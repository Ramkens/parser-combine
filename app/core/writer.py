"""Streaming output writers.

Each parser yields dict items; writer flushes them into a per-source .txt file
(line-per-record, human-readable) AND keeps minimal metadata for the XLSX packer.
We never accumulate the full dataset in RAM - rows are flushed to disk as they
arrive, and the XLSX is built from the same .txt files at the very end.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List

from app.core.logger import get_logger

log = get_logger("writer")


def _fmt_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    return json.dumps(v, ensure_ascii=False)


@dataclass
class SourceWriter:
    """Append-only writer for one source.

    Stores rows as JSONL on disk (cheap, streaming) AND a human-readable .txt
    in parallel. The XLSX packer reads back the JSONL.
    """

    source: str
    out_dir: Path
    columns: List[str]
    count: int = 0
    _txt_path: Path = field(init=False)
    _jsonl_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._txt_path = self.out_dir / f"{self.source}.txt"
        self._jsonl_path = self.out_dir / f"{self.source}.jsonl"
        # truncate at start of run
        self._txt_path.write_text("", encoding="utf-8")
        self._jsonl_path.write_text("", encoding="utf-8")

    @property
    def txt_path(self) -> Path:
        return self._txt_path

    @property
    def jsonl_path(self) -> Path:
        return self._jsonl_path

    def write(self, row: Dict[str, Any]) -> None:
        # human-readable block
        with self._txt_path.open("a", encoding="utf-8") as f:
            for col in self.columns:
                f.write(f"{col}: {_fmt_value(row.get(col))}\n")
            f.write("-" * 60 + "\n")
        # JSONL for downstream xlsx
        with self._jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.count += 1

    def write_many(self, rows: Iterable[Dict[str, Any]]) -> None:
        for r in rows:
            self.write(r)
