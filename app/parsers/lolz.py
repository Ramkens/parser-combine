"""Lolz.live forum search parser (web scraping, no auth).

Uses the public forum search page. Returns matched threads/posts/users.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.lolz")

_BASE = "https://lolz.live"


class LolzParser(BaseParser):
    name = "lolz"
    columns = ["title", "url", "author", "section", "snippet"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        for kw in (task.keywords or [""]):
            if produced >= task.limit:
                break
            page = 1
            while produced < task.limit:
                params = {"q": kw, "o": "date", "t": "post"}
                if page > 1:
                    params["page"] = str(page)
                try:
                    html = await self.http.get(f"{_BASE}/search/search", params=params)
                except Exception as e:
                    log.warning("lolz search '%s' page %s failed: %s", kw, page, e)
                    break
                rows = list(self._parse(html))
                if not rows:
                    break
                for r in rows:
                    if produced >= task.limit:
                        break
                    yield r
                    produced += 1
                page += 1
                if page > 10:
                    break

    def _parse(self, html: str) -> List[Dict[str, Any]]:
        tree = HTMLParser(html)
        out: List[Dict[str, Any]] = []
        for li in tree.css("li.searchResult, li.block-row, .search-result"):
            title_node = li.css_first("h3 a, .title a, a.PreviewTooltip")
            if not title_node:
                continue
            href = title_node.attributes.get("href", "")
            if href and not href.startswith("http"):
                href = f"{_BASE}/{href.lstrip('/')}"
            author_node = li.css_first(".meta a.username, .username")
            section_node = li.css_first(".meta .label, .meta span:nth-child(1)")
            snippet_node = li.css_first(".snippet, blockquote")
            out.append({
                "title": title_node.text(strip=True),
                "url": href,
                "author": author_node.text(strip=True) if author_node else "",
                "section": section_node.text(strip=True) if section_node else "",
                "snippet": (snippet_node.text(strip=True)[:500] if snippet_node else ""),
            })
        return out
