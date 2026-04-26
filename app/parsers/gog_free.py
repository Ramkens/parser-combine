"""GOG free games via the public catalog API."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.gog")


class GogFreeSource(BaseSource):
    name = "gog"
    display = "GOG (Free)"
    columns = ["id", "title", "url", "developers", "release"]
    interval = 1800.0

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        page = 1
        while page < 20:
            url = "https://catalog.gog.com/v1/catalog"
            params = {
                "limit": "48",
                "order": "desc:trending",
                "price": "between:0,0",
                "productType": "in:game,pack",
                "page": str(page),
            }
            try:
                data = await self.http.get_json(url, params=params)
            except Exception as e:
                log.warning("gog page %s failed: %s", page, e)
                return
            products = (data or {}).get("products") or []
            if not products:
                return
            for p in products:
                pid = p.get("id") or p.get("slug")
                if not pid:
                    continue
                yield (
                    f"gog:{pid}",
                    {
                        "id": pid,
                        "title": p.get("title") or "",
                        "url": f"https://www.gog.com{p.get('storeLink', '')}" if p.get("storeLink") else f"https://www.gog.com/game/{p.get('slug', '')}",
                        "developers": ", ".join(p.get("developers") or []),
                        "release": p.get("releaseDate") or "",
                    },
                )
            if page >= (data.get("pages") or 0):
                return
            page += 1
