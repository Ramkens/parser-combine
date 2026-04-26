"""Run a multi-source parse job concurrently with bounded concurrency."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from app.core.config import CONFIG
from app.core.http import HttpClient
from app.core.logger import get_logger
from app.core.writer import SourceWriter
from app.output.packer import pack_run
from app.parsers.base import ParseTask
from app.parsers.registry import REGISTRY

log = get_logger("orchestrator")


@dataclass
class RunResult:
    run_id: str
    run_dir: Path
    counts: Dict[str, int] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    duration: float = 0.0
    zip_path: Optional[Path] = None
    xlsx_path: Optional[Path] = None


ProgressCb = Callable[[str, int, int], Awaitable[None]]


async def run_parse(
    sources: List[str],
    keywords: List[str],
    *,
    limit_per_source: int = 100,
    extras: Optional[Dict[str, Dict[str, Any]]] = None,
    progress: Optional[ProgressCb] = None,
    parser_concurrency: int = 3,
) -> RunResult:
    sources = [s for s in sources if s in REGISTRY]
    if not sources:
        raise ValueError("no valid sources selected")
    extras = extras or {}
    started = time.time()
    run_id = time.strftime("%Y%m%d-%H%M%S")
    run_dir = (CONFIG.output_dir / run_id).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(parser_concurrency)
    counts: Dict[str, int] = {}
    errors: Dict[str, str] = {}

    async with HttpClient() as http:

        async def run_one(src: str) -> None:
            async with sem:
                cls = REGISTRY[src]
                parser = cls(http)
                writer = SourceWriter(source=src, out_dir=run_dir, columns=list(cls.columns))
                task = ParseTask(
                    keywords=keywords,
                    limit=limit_per_source,
                    extra=extras.get(src),
                )
                try:
                    log.info("[%s] start", src)
                    async for row in parser.fetch(task):
                        writer.write(row)
                        if progress and writer.count % 5 == 0:
                            await progress(src, writer.count, limit_per_source)
                    log.info("[%s] done: %s rows", src, writer.count)
                except Exception as e:
                    log.exception("[%s] failed: %s", src, e)
                    errors[src] = f"{type(e).__name__}: {e}"
                finally:
                    counts[src] = writer.count
                    if progress:
                        try:
                            await progress(src, writer.count, limit_per_source)
                        except Exception:
                            pass

        await asyncio.gather(*(run_one(s) for s in sources))

    # Run metadata
    readme = run_dir / "README.txt"
    readme.write_text(
        "Parser-combine run\n"
        f"id: {run_id}\n"
        f"keywords: {', '.join(keywords) or '(none)'}\n"
        f"sources: {', '.join(sources)}\n"
        f"limit_per_source: {limit_per_source}\n"
        f"counts: {counts}\n"
        f"errors: {errors}\n",
        encoding="utf-8",
    )
    zip_path, xlsx_path = pack_run(run_dir, sources)
    duration = time.time() - started
    log.info("run %s done in %.1fs: %s", run_id, duration, counts)
    return RunResult(
        run_id=run_id,
        run_dir=run_dir,
        counts=counts,
        errors=errors,
        duration=duration,
        zip_path=zip_path,
        xlsx_path=xlsx_path,
    )
