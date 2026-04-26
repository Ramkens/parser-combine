"""GamerPower public API — all current giveaways (free games, DLC, in-game items)."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.gp")


class GamerPowerSource(BaseSource):
    name = "gamerpower"
    display = "GamerPower (Giveaways)"
    columns = ["id", "title", "type", "platforms", "url", "worth", "end_date", "description"]
    interval = 900.0  # 15 min

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        try:
            data = await self.http.get_json(
                "https://www.gamerpower.com/api/giveaways",
                params={"sort-by": "date"},
            )
        except Exception as e:
            log.warning("gamerpower fetch failed: %s", e)
            return
        if not isinstance(data, list):
            return
        for g in data:
            gid = g.get("id")
            if gid is None:
                continue
            yield (
                f"gp:{gid}",
                {
                    "id": gid,
                    "title": g.get("title") or "",
                    "type": g.get("type") or "",
                    "platforms": g.get("platforms") or "",
                    "url": g.get("open_giveaway_url") or g.get("gamerpower_url") or "",
                    "worth": g.get("worth") or "",
                    "end_date": g.get("end_date") or "",
                    "description": (g.get("description") or "")[:400],
                },
            )
