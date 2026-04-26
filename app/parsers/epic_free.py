"""Epic Games Store free promotions via the public storefront API."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.epic")


class EpicFreeSource(BaseSource):
    name = "epic"
    display = "Epic Games Store (Free)"
    columns = ["title", "url", "publisher", "promotion", "description"]
    interval = 1800.0

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        url = (
            "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
            "?locale=en-US&country=US&allowCountries=US"
        )
        try:
            data = await self.http.get_json(url)
        except Exception as e:
            log.warning("epic fetch failed: %s", e)
            return
        elements = (
            ((data or {}).get("data") or {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )
        for el in elements:
            promos = el.get("promotions") or {}
            promo_list = (promos.get("promotionalOffers") or []) + (promos.get("upcomingPromotionalOffers") or [])
            promo_state = "none"
            if promos.get("promotionalOffers"):
                promo_state = "active"
            elif promos.get("upcomingPromotionalOffers"):
                promo_state = "upcoming"
            slug = ""
            for m in (el.get("offerMappings") or []):
                if m.get("pageSlug"):
                    slug = m["pageSlug"]
                    break
            if not slug:
                # fallback to catalogNs/mappings or productSlug
                cat = el.get("catalogNs") or {}
                for m in cat.get("mappings") or []:
                    if m.get("pageSlug"):
                        slug = m["pageSlug"]
                        break
            if not slug:
                slug = el.get("productSlug") or el.get("urlSlug") or ""
            slug = (slug or "").split("/")[0]
            url2 = f"https://store.epicgames.com/en-US/p/{slug}" if slug else ""
            offer_id = el.get("id") or el.get("offerId") or el.get("title")
            yield (
                f"epic:{offer_id}:{promo_state}",
                {
                    "title": el.get("title") or "",
                    "url": url2,
                    "publisher": el.get("seller", {}).get("name") or "",
                    "promotion": promo_state,
                    "description": (el.get("description") or "")[:500],
                },
            )
