"""Hacker News search via the Algolia public API."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.hn")


class HackerNewsParser(BaseParser):
    name = "hackernews"
    columns = ["title", "url", "author", "points", "comments", "created_at"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        per_page = 50
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            page = 0
            while produced < task.limit and page < 20:
                params = {
                    "query": kw,
                    "tags": "story",
                    "hitsPerPage": str(per_page),
                    "page": str(page),
                }
                try:
                    data = await self.http.get_json(
                        "https://hn.algolia.com/api/v1/search_by_date", params=params
                    )
                except Exception as e:
                    log.warning("hn page %s failed: %s", page, e)
                    break
                hits = data.get("hits") or []
                if not hits:
                    break
                for h in hits:
                    if produced >= task.limit:
                        break
                    oid = h.get("objectID") or ""
                    yield {
                        "title": h.get("title") or h.get("story_title") or "",
                        "url": h.get("url") or (f"https://news.ycombinator.com/item?id={oid}" if oid else ""),
                        "author": h.get("author") or "",
                        "points": h.get("points") or 0,
                        "comments": h.get("num_comments") or 0,
                        "created_at": h.get("created_at") or "",
                    }
                    produced += 1
                page += 1
                if page >= data.get("nbPages", 0):
                    break
