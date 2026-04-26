"""HeadHunter vacancies parser via the public api.hh.ru."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.hh")


class HHParser(BaseParser):
    name = "hh"
    columns = ["title", "company", "salary", "area", "url", "snippet"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        per_page = 50
        for kw in (task.keywords or [task.opt("query") or "python"]):
            if produced >= task.limit:
                break
            page = 0
            while produced < task.limit and page < 20:
                params: Dict[str, Any] = {
                    "text": kw,
                    "per_page": per_page,
                    "page": page,
                }
                area = task.opt("area")
                if area:
                    params["area"] = area
                try:
                    data = await self.http.get_json("https://api.hh.ru/vacancies", params=params)
                except Exception as e:
                    log.warning("hh page %s failed: %s", page, e)
                    break
                items = data.get("items") or []
                if not items:
                    break
                for v in items:
                    if produced >= task.limit:
                        break
                    salary = ""
                    s = v.get("salary") or {}
                    if s:
                        parts = []
                        if s.get("from"):
                            parts.append(f"от {s['from']}")
                        if s.get("to"):
                            parts.append(f"до {s['to']}")
                        if s.get("currency"):
                            parts.append(s["currency"])
                        salary = " ".join(parts)
                    snippet = v.get("snippet") or {}
                    yield {
                        "title": v.get("name") or "",
                        "company": (v.get("employer") or {}).get("name") or "",
                        "salary": salary,
                        "area": (v.get("area") or {}).get("name") or "",
                        "url": v.get("alternate_url") or v.get("url") or "",
                        "snippet": (snippet.get("requirement") or "").replace("\n", " ")[:300],
                    }
                    produced += 1
                page += 1
                if page >= data.get("pages", 0):
                    break
