"""Avito search parser (mobile web).

Avito has aggressive anti-bot. We try the mobile web layer which is usually
more permissive, but still expect occasional 429/403. The base http retry is
already in place; we just bail out gracefully.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict
from urllib.parse import quote

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.avito")


class AvitoParser(BaseParser):
    name = "avito"
    columns = ["title", "url", "price", "location", "description"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        city = task.opt("city") or "rossiya"
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            page = 1
            while produced < task.limit and page <= 5:
                url = f"https://www.avito.ru/{city}?q={quote(kw)}&p={page}"
                try:
                    html = await self.http.get(url)
                except Exception as e:
                    log.warning("avito page %s failed: %s", page, e)
                    break
                tree = HTMLParser(html)
                items = tree.css("div[data-marker='item']")
                if not items:
                    break
                for it in items:
                    if produced >= task.limit:
                        break
                    title_a = it.css_first("a[data-marker='item-title']")
                    href = title_a.attributes.get("href", "") if title_a else ""
                    if href and not href.startswith("http"):
                        href = "https://www.avito.ru" + href
                    price = it.css_first("[data-marker='item-price']")
                    location = it.css_first("[class*='geo-root']")
                    desc = it.css_first("[class*='item-description']")
                    yield {
                        "title": title_a.text(strip=True) if title_a else "",
                        "url": href,
                        "price": price.text(strip=True) if price else "",
                        "location": location.text(strip=True) if location else "",
                        "description": (desc.text(strip=True)[:300] if desc else ""),
                    }
                    produced += 1
                page += 1
