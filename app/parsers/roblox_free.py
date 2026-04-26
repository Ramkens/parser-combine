"""Roblox catalog free items via catalog.roblox.com.

Sweeps the public catalog filtered to MaxPrice=0 across the supported
categories. Stable id = AssetID.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.roblox")


# Category IDs from Roblox catalog API:
# 1=Featured, 2=Collectibles, 3=Clothing, 4=BodyParts, 5=Gear,
# 11=Accessories, 12=AvatarAnimations, 13=CommunityCreations
_CATEGORIES = [3, 11, 4, 12]


class RobloxFreeSource(BaseSource):
    name = "roblox"
    display = "Roblox (Free)"
    columns = ["assetId", "name", "type", "creator", "url", "thumbnail"]
    interval = 600.0  # 10 min

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        for category in _CATEGORIES:
            cursor: str | None = None
            page = 0
            while page < 30:
                params = {
                    "Category": str(category),
                    "Limit": "120",
                    "MaxPrice": "0",
                    "MinPrice": "0",
                    "SortType": "3",  # 3 = recently updated
                }
                if cursor:
                    params["Cursor"] = cursor
                try:
                    data = await self.http.get_json(
                        "https://catalog.roblox.com/v1/search/items/details",
                        params=params,
                    )
                except Exception as e:
                    log.warning("roblox cat=%s page=%s failed: %s", category, page, e)
                    break
                items = (data or {}).get("data") or []
                if not items:
                    break
                for it in items:
                    asset_id = it.get("id") or it.get("itemId") or it.get("assetId")
                    if not asset_id:
                        continue
                    yield (
                        f"asset:{asset_id}",
                        {
                            "assetId": asset_id,
                            "name": it.get("name") or "",
                            "type": it.get("itemType") or it.get("assetType") or "",
                            "creator": (it.get("creatorName") or it.get("creatorTargetId", "")),
                            "url": f"https://www.roblox.com/catalog/{asset_id}/",
                            "thumbnail": "",
                        },
                    )
                cursor = (data or {}).get("nextPageCursor")
                if not cursor:
                    break
                page += 1
