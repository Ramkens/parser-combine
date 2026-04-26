"""CLI entrypoint: `python -m app.cli --sources wb,steam --keywords "телефон,скидка"`."""
from __future__ import annotations

import argparse
import asyncio
import sys

from app.core.logger import get_logger
from app.orchestrator import run_parse
from app.parsers.registry import all_keys

log = get_logger("cli")


def _split_csv(s: str) -> list[str]:
    return [p.strip() for p in s.split(",") if p.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="parser-combine CLI")
    p.add_argument("--sources", default=",".join(all_keys()),
                   help=f"CSV list. available: {','.join(all_keys())}")
    p.add_argument("--keywords", default="", help="CSV list of keywords")
    p.add_argument("--limit", type=int, default=50, help="per-source limit")
    args = p.parse_args()

    sources = _split_csv(args.sources)
    keywords = _split_csv(args.keywords)

    res = asyncio.run(run_parse(sources, keywords, limit_per_source=args.limit))
    print(f"\nrun: {res.run_id}\ncounts: {res.counts}\nerrors: {res.errors}")
    print(f"zip: {res.zip_path}\nxlsx: {res.xlsx_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
