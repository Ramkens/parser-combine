"""Reddit search via the public .json endpoints (no auth)."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.reddit")


class RedditParser(BaseParser):
    name = "reddit"
    columns = ["title", "url", "subreddit", "author", "score", "permalink"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        per_page = 100
        sub = task.opt("subreddit")  # restrict to one subreddit if provided
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            after: str | None = None
            for _ in range(10):
                if produced >= task.limit:
                    break
                params: Dict[str, Any] = {
                    "q": kw,
                    "sort": "new",
                    "limit": per_page,
                    "raw_json": 1,
                }
                if after:
                    params["after"] = after
                if sub:
                    params["restrict_sr"] = "on"
                base = f"https://www.reddit.com/r/{sub}/search.json" if sub else "https://www.reddit.com/search.json"
                try:
                    data = await self.http.get_json(base, params=params)
                except Exception as e:
                    log.warning("reddit page failed: %s", e)
                    break
                children = (data.get("data") or {}).get("children") or []
                if not children:
                    break
                for c in children:
                    if produced >= task.limit:
                        break
                    d = c.get("data") or {}
                    yield {
                        "title": d.get("title") or "",
                        "url": d.get("url") or "",
                        "subreddit": d.get("subreddit") or "",
                        "author": d.get("author") or "",
                        "score": d.get("score") or 0,
                        "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                    }
                    produced += 1
                after = (data.get("data") or {}).get("after")
                if not after:
                    break
