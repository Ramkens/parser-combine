"""Wildberries parser via their public catalog search API.

We pull cheap items by sorting by price ascending, optional min/max price filter
and discount filter. The search.wb.ru endpoint returns JSON without auth.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.wb")


def _wb_url(article: int) -> str:
    return f"https://www.wildberries.ru/catalog/{article}/detail.aspx"


class WildberriesParser(BaseParser):
    name = "wildberries"
    columns = ["title", "price", "old_price", "discount", "rating", "url", "brand"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        # WB filters: priceU is in kopecks (price * 100). Default cheap = under 500₽.
        max_price_rub = int(task.opt("max_price") or 500)
        min_discount = int(task.opt("min_discount") or 0)
        priceU_to = max_price_rub * 100
        for kw in (task.keywords or ["акция"]):
            if produced >= task.limit:
                break
            page = 1
            # Some IPs get 429 from search.wb.ru — u-search.wb.ru is an
            # alternative endpoint with the same shape, used as fallback.
            hosts = ["https://search.wb.ru", "https://u-search.wb.ru"]
            while produced < task.limit and page <= 30:
                params = {
                    "ab_testing": "false",
                    "appType": "1",
                    "curr": "rub",
                    "dest": "-1257786",
                    "query": kw,
                    "resultset": "catalog",
                    "sort": "priceup",
                    "spp": "30",
                    "suppressSpellcheck": "false",
                    "page": str(page),
                    "priceU": f";{priceU_to}",
                }
                headers = {
                    "Origin": "https://www.wildberries.ru",
                    "Referer": "https://www.wildberries.ru/",
                    "Accept": "application/json",
                }
                data = None
                for host in hosts:
                    try:
                        data = await self.http.get_json(
                            f"{host}/exactmatch/ru/common/v5/search",
                            params=params,
                            headers=headers,
                        )
                        if data:
                            break
                    except Exception as e:
                        log.debug("wb host %s failed: %s", host, e)
                if data is None:
                    log.warning("wildberries page %s failed (all hosts)", page)
                    break
                items = ((data or {}).get("data") or {}).get("products") or []
                if not items:
                    break
                for p in items:
                    if produced >= task.limit:
                        break
                    sale_price = (p.get("salePriceU") or p.get("priceU") or 0) / 100
                    old_price = (p.get("priceU") or 0) / 100
                    discount = 0
                    if old_price and sale_price and sale_price < old_price:
                        discount = round((1 - sale_price / old_price) * 100)
                    if discount < min_discount:
                        continue
                    if sale_price and sale_price > max_price_rub:
                        continue
                    article = p.get("id") or 0
                    yield {
                        "title": p.get("name") or "",
                        "price": sale_price,
                        "old_price": old_price,
                        "discount": discount,
                        "rating": p.get("rating") or p.get("reviewRating") or "",
                        "url": _wb_url(article) if article else "",
                        "brand": p.get("brand") or "",
                    }
                    produced += 1
                page += 1
