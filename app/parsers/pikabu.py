"""Pikabu posts search (web, no auth)."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict
from urllib.parse import quote

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.pikabu")


class PikabuParser(BaseParser):
    name = "pikabu"
    columns = ["title", "url", "author", "rating", "snippet"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            page = 1
            while produced < task.limit and page <= 10:
                url = f"https://pikabu.ru/search?q={quote(kw)}&D=0&page={page}"
                try:
                    html = await self.http.get(url)
                except Exception as e:
                    log.warning("pikabu page %s failed: %s", page, e)
                    break
                tree = HTMLParser(html)
                stories = tree.css("article.story")
                if not stories:
                    break
                for s in stories:
                    if produced >= task.limit:
                        break
                    title_a = s.css_first(".story__title-link")
                    author_a = s.css_first(".user__nick")
                    rating = s.css_first(".story__rating-count")
                    snippet = s.css_first(".story-block_type_text")
                    yield {
                        "title": title_a.text(strip=True) if title_a else "",
                        "url": title_a.attributes.get("href", "") if title_a else "",
                        "author": author_a.text(strip=True) if author_a else "",
                        "rating": rating.text(strip=True) if rating else "",
                        "snippet": (snippet.text(strip=True)[:400] if snippet else ""),
                    }
                    produced += 1
                page += 1
