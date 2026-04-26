"""Telegram public web parser.

Uses https://t.me/s/{channel} preview pages (no API). Channels can be supplied
explicitly via task.extra['channels']; otherwise we fall back to a small
popular-Russian-channels list. Messages, channel names and links are scraped
and filtered by keywords (any-of).
"""
from __future__ import annotations

import re
from typing import Any, AsyncIterator, Dict, Iterable, List

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.telegram")


_DEFAULT_CHANNELS: List[str] = [
    "durov", "telegram", "tginfo", "tginfo_ru",
    "ru2ch", "habr_com", "lentaruofficial", "rbc_news", "meduzalive",
    "stalin_gulag", "varlamov_news", "breakingmash", "readovkanews",
    "mash", "tass_agency",
]


def _matches(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    low = text.lower()
    return any(k.strip().lower() in low for k in keywords if k.strip())


class TelegramWebParser(BaseParser):
    name = "telegram"
    columns = ["channel", "title", "username", "url", "description", "matched_text"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        channels: Iterable[str] = task.opt("channels") or _DEFAULT_CHANNELS
        produced = 0
        for ch in channels:
            if produced >= task.limit:
                break
            ch = ch.strip().lstrip("@").lstrip("/")
            if not ch:
                continue
            try:
                async for row in self._channel(ch, task):
                    yield row
                    produced += 1
                    if produced >= task.limit:
                        break
            except Exception as e:
                log.warning("telegram channel %s failed: %s", ch, e)

    async def _channel(self, ch: str, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        url = f"https://t.me/s/{ch}"
        html = await self.http.get(url)
        tree = HTMLParser(html)

        title_node = tree.css_first(".tgme_channel_info_header_title span")
        desc_node = tree.css_first(".tgme_channel_info_description")
        title = title_node.text(strip=True) if title_node else ch
        description = desc_node.text(strip=True) if desc_node else ""

        # Channel-card row (always emit so user sees the channel itself)
        if _matches(f"{title} {description} {ch}", task.keywords):
            yield {
                "channel": title,
                "title": title,
                "username": f"@{ch}",
                "url": f"https://t.me/{ch}",
                "description": description,
                "matched_text": "",
            }

        for msg in tree.css(".tgme_widget_message"):
            text_node = msg.css_first(".tgme_widget_message_text")
            text = text_node.text(strip=True) if text_node else ""
            if not _matches(text, task.keywords):
                continue
            link_node = msg.css_first(".tgme_widget_message_date")
            link = link_node.attributes.get("href", "") if link_node else ""
            yield {
                "channel": title,
                "title": (text[:120] + "…") if len(text) > 120 else text,
                "username": f"@{ch}",
                "url": link or f"https://t.me/{ch}",
                "description": description,
                "matched_text": text[:1000],
            }

    @staticmethod
    def clean(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()
