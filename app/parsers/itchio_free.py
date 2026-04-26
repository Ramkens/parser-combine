"""itch.io free games via the public browse pages."""
from __future__ import annotations

import re
from typing import Any, AsyncIterator, Dict, Tuple

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.itchio")


class ItchIoFreeSource(BaseSource):
    name = "itchio"
    display = "itch.io (Free)"
    columns = ["id", "title", "url", "author", "genre", "thumbnail"]
    interval = 1200.0

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        page = 1
        while page < 30:
            url = f"https://itch.io/games/free/page/{page}"
            try:
                html = await self.http.get(url)
            except Exception as e:
                log.warning("itchio page %s failed: %s", page, e)
                return
            tree = HTMLParser(html)
            cells = tree.css(".game_cell")
            if not cells:
                return
            for cell in cells:
                gid = cell.attributes.get("data-game_id") or ""
                title_node = cell.css_first(".title.game_link")
                if not title_node:
                    continue
                href = title_node.attributes.get("href", "")
                author_node = cell.css_first(".game_author a")
                genre_node = cell.css_first(".game_genre")
                thumb_node = cell.css_first(".thumb_link img")
                yield (
                    f"itch:{gid or href}",
                    {
                        "id": gid,
                        "title": title_node.text(strip=True),
                        "url": href,
                        "author": author_node.text(strip=True) if author_node else "",
                        "genre": genre_node.text(strip=True) if genre_node else "",
                        "thumbnail": thumb_node.attributes.get("data-lazy_src", "") if thumb_node else "",
                    },
                )
            page += 1
