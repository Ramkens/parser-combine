"""Steam search parser.

Uses the public store search HTML/JSON endpoint. By default filters to free
items (maxprice=free); pass extras['maxprice'] to override (e.g. "10").
Keywords are used as search query directly when present.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.steam")


class SteamParser(BaseParser):
    name = "steam"
    columns = ["title", "url", "description", "release", "review"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        page_size = 50
        queries = task.keywords or [""]
        for query in queries:
            if produced >= task.limit:
                break
            page = 1
            while produced < task.limit and page <= 20:
                start = (page - 1) * page_size
                url = "https://store.steampowered.com/search/results/"
                params = {
                    "query": query,
                    "start": str(start),
                    "count": str(page_size),
                    "maxprice": str(task.opt("maxprice") or "free"),
                    "infinite": "1",
                    "cc": task.opt("cc") or "ru",
                    "l": "russian",
                }
                try:
                    data = await self.http.get_json(url, params=params)
                except Exception as e:
                    log.warning("steam search page %s failed: %s", page, e)
                    break
                html = data.get("results_html") if isinstance(data, dict) else None
                if not html:
                    break
                tree = HTMLParser(html)
                cards = tree.css("a.search_result_row")
                if not cards:
                    break
                for card in cards:
                    if produced >= task.limit:
                        break
                    title = card.css_first(".title")
                    desc = card.css_first(".search_released")
                    review = card.css_first(".search_review_summary")
                    href = card.attributes.get("href", "")
                    title_txt = title.text(strip=True) if title else ""
                    yield {
                        "title": title_txt,
                        "url": href,
                        "description": "",
                        "release": desc.text(strip=True) if desc else "",
                        "review": review.attributes.get("data-tooltip-html", "") if review else "",
                    }
                    produced += 1
                page += 1
