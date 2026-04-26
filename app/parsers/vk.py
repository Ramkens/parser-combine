"""VK public groups parser via m.vk.com (no auth).

Provide group screen-names via task.extra['groups']; otherwise we fall back to
a small default list. Posts are filtered by keywords.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.vk")


_DEFAULT_GROUPS: List[str] = ["habr", "ria", "lentaru", "tjournal", "vc.ru"]


def _matches(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    low = text.lower()
    return any(k.strip().lower() in low for k in keywords if k.strip())


class VKParser(BaseParser):
    name = "vk"
    columns = ["group", "url", "post_url", "text"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        groups: List[str] = task.opt("groups") or _DEFAULT_GROUPS
        produced = 0
        for g in groups:
            if produced >= task.limit:
                break
            g = g.strip().lstrip("@").lstrip("/")
            if not g:
                continue
            url = f"https://m.vk.com/{g}"
            try:
                html = await self.http.get(url)
            except Exception as e:
                log.warning("vk group %s failed: %s", g, e)
                continue
            tree = HTMLParser(html)
            posts = tree.css("div.wall_item")
            if not posts:
                # m.vk renders inside iframe sometimes; fall back to /wall view
                continue
            for post in posts:
                if produced >= task.limit:
                    break
                text_node = post.css_first(".pi_text")
                text = text_node.text(strip=True) if text_node else ""
                if not _matches(text, task.keywords):
                    continue
                link_node = post.css_first("a.pi_medium_link, a.PostHeader__link, a[href*='/wall']")
                href = link_node.attributes.get("href", "") if link_node else ""
                if href and not href.startswith("http"):
                    href = "https://m.vk.com" + href
                yield {
                    "group": g,
                    "url": url,
                    "post_url": href,
                    "text": text[:1000],
                }
                produced += 1
