"""FreeToGame public API — aggregator of free-to-play games."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.f2g")


class FreeToGameSource(BaseSource):
    name = "freetogame"
    display = "FreeToGame.com"
    columns = ["id", "title", "url", "platform", "genre", "publisher", "release", "thumbnail"]
    interval = 3600.0  # whole list every hour

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        try:
            data = await self.http.get_json("https://www.freetogame.com/api/games")
        except Exception as e:
            log.warning("freetogame fetch failed: %s", e)
            return
        if not isinstance(data, list):
            return
        for g in data:
            gid = g.get("id")
            if not gid:
                continue
            yield (
                f"f2g:{gid}",
                {
                    "id": gid,
                    "title": g.get("title") or "",
                    "url": g.get("game_url") or g.get("freetogame_profile_url") or "",
                    "platform": g.get("platform") or "",
                    "genre": g.get("genre") or "",
                    "publisher": g.get("publisher") or "",
                    "release": g.get("release_date") or "",
                    "thumbnail": g.get("thumbnail") or "",
                },
            )
