"""2GIS parser using the public catalog widget endpoint.

The 2GIS website itself uses the same JSON API, and a public anonymous key is
fine for low-volume reads. Defaults to Moscow if no city supplied.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.2gis")

# This is a publicly used anonymous key for the catalog widget.
_PUBLIC_KEY = "6e7e1929-4ea9-4a5d-8c05-d601860389bd"
_FIELDS = ",".join([
    "items.point", "items.adm_div", "items.address", "items.name_ex",
    "items.contact_groups", "items.rubrics", "items.org",
])


class TwoGISParser(BaseParser):
    name = "2gis"
    columns = ["name", "address", "phone", "site", "category", "city", "url"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        city = task.opt("city") or "Москва"
        page_size = 50
        produced = 0
        for keyword in (task.keywords or [task.opt("query") or "Кафе"]):
            if produced >= task.limit:
                break
            page = 1
            while produced < task.limit:
                url = "https://catalog.api.2gis.com/3.0/items"
                params = {
                    "q": f"{keyword}",
                    "city": city,
                    "fields": _FIELDS,
                    "page": str(page),
                    "page_size": str(page_size),
                    "key": _PUBLIC_KEY,
                }
                try:
                    data = await self.http.get_json(url, params=params)
                except Exception as e:
                    log.warning("2gis page %s failed: %s", page, e)
                    break
                items = (data.get("result") or {}).get("items") or []
                if not items:
                    break
                for it in items:
                    if produced >= task.limit:
                        break
                    yield self._row(it, city)
                    produced += 1
                page += 1
                if len(items) < page_size:
                    break

    @staticmethod
    def _row(it: Dict[str, Any], city: str) -> Dict[str, Any]:
        contacts = it.get("contact_groups") or []
        phone = ""
        site = ""
        for grp in contacts:
            for c in grp.get("contacts") or []:
                ctype = c.get("type")
                value = c.get("value") or ""
                if ctype == "phone" and not phone:
                    phone = value
                elif ctype == "website" and not site:
                    site = value
        rubrics = it.get("rubrics") or []
        category = ", ".join(r.get("name", "") for r in rubrics if r.get("name"))
        oid = it.get("id") or ""
        return {
            "name": it.get("name") or it.get("name_ex", {}).get("primary") or "",
            "address": it.get("address_name") or it.get("address", {}).get("name") or "",
            "phone": phone,
            "site": site,
            "category": category,
            "city": city,
            "url": f"https://2gis.ru/firm/{oid}" if oid else "",
        }
