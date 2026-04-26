"""Pack run artefacts into a ZIP and a multi-sheet XLSX.

Both reads from the per-source files written by SourceWriter on the fly; we
intentionally don't keep rows in memory. The XLSX is built lazily, sheet by
sheet, streaming JSONL into openpyxl rows.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable, List, Tuple

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from app.core.logger import get_logger
from app.parsers.registry import REGISTRY

log = get_logger("output.packer")


def _iter_jsonl(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def build_zip(run_dir: Path, sources: List[str], zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for src in sources:
            txt = run_dir / f"{src}.txt"
            if txt.exists():
                zf.write(txt, arcname=f"{src}.txt")
        readme = run_dir / "README.txt"
        if readme.exists():
            zf.write(readme, arcname="README.txt")
    return zip_path


def build_xlsx(run_dir: Path, sources: List[str], xlsx_path: Path) -> Path:
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook(write_only=True)
    for src in sources:
        cls = REGISTRY.get(src)
        cols = list(cls.columns) if cls else []
        ws = wb.create_sheet(title=src[:31] or "sheet")
        if cols:
            ws.append(cols)
        for row in _iter_jsonl(run_dir / f"{src}.jsonl"):
            ws.append([row.get(c, "") for c in cols] if cols else list(row.values()))
    if not wb.sheetnames:
        wb.create_sheet(title="empty")
    wb.save(xlsx_path)
    return xlsx_path


def pack_run(run_dir: Path, sources: List[str]) -> Tuple[Path, Path]:
    zip_path = run_dir / "output.zip"
    xlsx_path = run_dir / "output.xlsx"
    build_zip(run_dir, sources, zip_path)
    build_xlsx(run_dir, sources, xlsx_path)
    return zip_path, xlsx_path
