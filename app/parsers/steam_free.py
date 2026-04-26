"""Steam: all Free-to-Play / free apps via the public store search.

Sweeps the entire `maxprice=free` listing in pages of 50 until exhausted.
Stable id = Steam appid.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.steam")


class SteamFreeSource(BaseSource):
    name = "steam"
    display = "Steam (Free)"
    columns = ["appid", "title", "url", "release", "review", "tags"]
    interval = 1800.0  # full sweep every 30 min

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        page_size = 50
        page = 0
        # Steam's "maxprice=free" includes both F2P and 100%-discounted titles.
        while page < 200:
            start = page * page_size
            url = "https://store.steampowered.com/search/results/"
            params = {
                "query": "",
                "start": str(start),
                "count": str(page_size),
                "maxprice": "free",
                "infinite": "1",
                "cc": "ru",
                "l": "english",
            }
            try:
                data = await self.http.get_json(url, params=params)
            except Exception as e:
                log.warning("steam page %s failed: %s", page, e)
                break
            html = (data or {}).get("results_html") or ""
            if not html:
                break
            tree = HTMLParser(html)
            cards = tree.css("a.search_result_row")
            if not cards:
                break
            yielded = 0
            for card in cards:
                appid = card.attributes.get("data-ds-appid") or ""
                if not appid:
                    appid = card.attributes.get("data-ds-bundleid") or ""
                if not appid:
                    continue
                title_node = card.css_first(".title")
                review_node = card.css_first(".search_review_summary")
                rel_node = card.css_first(".search_released")
                href = card.attributes.get("href", "")
                tags = card.attributes.get("data-ds-tagids", "")
                yield (
                    f"app:{appid}",
                    {
                        "appid": appid,
                        "title": title_node.text(strip=True) if title_node else "",
                        "url": href,
                        "release": rel_node.text(strip=True) if rel_node else "",
                        "review": (review_node.attributes.get("data-tooltip-html", "") if review_node else ""),
                        "tags": tags,
                    },
                )
                yielded += 1
            if yielded == 0:
                break
            page += 1
