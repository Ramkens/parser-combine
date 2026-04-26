"""Habr.com search via RSS feed."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict
from urllib.parse import quote

import feedparser  # type: ignore

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.habr")


class HabrParser(BaseParser):
    name = "habr"
    columns = ["title", "url", "author", "published", "summary"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            url = (
                f"https://habr.com/ru/rss/search/?q={quote(kw)}&target_type=posts&order=date"
                if kw else "https://habr.com/ru/rss/articles/"
            )
            try:
                xml = await self.http.get(url)
            except Exception as e:
                log.warning("habr feed for %r failed: %s", kw, e)
                continue
            feed = feedparser.parse(xml)
            for entry in feed.entries:
                if produced >= task.limit:
                    break
                yield {
                    "title": getattr(entry, "title", ""),
                    "url": getattr(entry, "link", ""),
                    "author": getattr(entry, "author", ""),
                    "published": getattr(entry, "published", ""),
                    "summary": (getattr(entry, "summary", "") or "")[:500],
                }
                produced += 1
