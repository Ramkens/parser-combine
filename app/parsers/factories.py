"""Generic source factories.

Most of our 1000+ sources fall into 4 patterns:
  - Reddit subreddit (.json public)
  - Telegram public channel web preview (t.me/s/<channel>)
  - RSS/Atom feed (feedparser)
  - Web JSON API endpoint with simple list-of-items shape

These factories let us instantiate hundreds of sources from data files.
"""
from __future__ import annotations

import re
import time
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, Type

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("factory")


def _safe_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()


# ────────────────────────────────────────────────────────────────────────────
# Reddit subreddit
# ────────────────────────────────────────────────────────────────────────────

def make_reddit_sub(
    sub: str,
    category: str = "deals",
    interval: float = 900.0,
    title_must_match: Optional[str] = None,
) -> Type[BaseSource]:
    """Each subreddit becomes its own source."""
    needle = title_must_match.lower() if title_must_match else None
    src_name = f"reddit_{_safe_name(sub)}"
    _cat = category

    class _RedditSub(BaseSource):
        name = src_name
        category = _cat
        display = f"Reddit /r/{sub}"
        interval = 900.0
        columns = ["id", "title", "url", "subreddit", "permalink", "author", "score", "created"]

        async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
            after: Optional[str] = None
            for _ in range(2):
                params: Dict[str, Any] = {"limit": 100, "raw_json": 1}
                if after:
                    params["after"] = after
                try:
                    data = await self.http.get_json(
                        f"https://www.reddit.com/r/{sub}/new.json",
                        params=params,
                        headers={"User-Agent": "parser-combine/1.0 (by u/anon)"},
                    )
                except Exception as e:
                    log.debug("reddit /r/%s failed: %s", sub, e)
                    return
                children = (data.get("data") or {}).get("children") or []
                if not children:
                    return
                for c in children:
                    d = c.get("data") or {}
                    pid = d.get("id")
                    if not pid:
                        continue
                    title = d.get("title") or ""
                    if needle and needle not in title.lower():
                        continue
                    yield (
                        f"r:{sub}:{pid}",
                        {
                            "id": pid,
                            "title": title,
                            "url": d.get("url") or "",
                            "subreddit": sub,
                            "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                            "author": d.get("author") or "",
                            "score": d.get("score") or 0,
                            "created": d.get("created_utc") or "",
                        },
                    )
                after = (data.get("data") or {}).get("after")
                if not after:
                    return

    _RedditSub.__name__ = f"RedditSub_{_safe_name(sub)}"
    _RedditSub.interval = interval
    _RedditSub.category = category
    return _RedditSub


# ────────────────────────────────────────────────────────────────────────────
# Telegram channel via web preview (t.me/s/<channel>)
# ────────────────────────────────────────────────────────────────────────────

def make_tg_channel(
    channel: str,
    category: str = "tg",
    interval: float = 1200.0,
) -> Type[BaseSource]:
    src_name = f"tg_{_safe_name(channel)}"
    _cat = category

    class _TgChannel(BaseSource):
        name = src_name
        category = _cat
        display = f"Telegram @{channel}"
        interval = 1200.0
        columns = ["id", "channel", "url", "datetime", "text"]

        async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
            try:
                html = await self.http.get(f"https://t.me/s/{channel}")
            except Exception as e:
                log.debug("tg @%s failed: %s", channel, e)
                return
            tree = HTMLParser(html)
            posts = tree.css(".tgme_widget_message_wrap .tgme_widget_message")
            if not posts:
                return
            for p in posts:
                post_id = p.attributes.get("data-post") or ""
                if not post_id:
                    continue
                href_node = p.css_first("a.tgme_widget_message_date")
                href = href_node.attributes.get("href", "") if href_node else f"https://t.me/{post_id}"
                time_node = p.css_first("a.tgme_widget_message_date time")
                dt = time_node.attributes.get("datetime", "") if time_node else ""
                text_node = p.css_first(".tgme_widget_message_text")
                text = text_node.text(strip=True)[:1500] if text_node else ""
                if not text:
                    continue
                yield (
                    f"tg:{post_id}",
                    {
                        "id": post_id,
                        "channel": channel,
                        "url": href,
                        "datetime": dt,
                        "text": text,
                    },
                )

    _TgChannel.__name__ = f"TgChannel_{_safe_name(channel)}"
    _TgChannel.interval = interval
    _TgChannel.category = category
    return _TgChannel


# ────────────────────────────────────────────────────────────────────────────
# RSS / Atom feed
# ────────────────────────────────────────────────────────────────────────────

def make_rss(
    rss_url: str,
    name: str,
    display: Optional[str] = None,
    category: str = "rss",
    interval: float = 1200.0,
    title_must_match: Optional[str] = None,
) -> Type[BaseSource]:
    needle = title_must_match.lower() if title_must_match else None
    src_name = f"rss_{_safe_name(name)}"
    _cat = category
    _disp = display or name

    class _Rss(BaseSource):
        name = src_name
        category = _cat
        display = _disp
        interval = 1200.0
        columns = ["id", "title", "url", "feed", "published", "summary"]

        async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
            import feedparser
            try:
                raw = await self.http.get(rss_url)
            except Exception as e:
                log.debug("rss %s failed: %s", rss_url, e)
                return
            try:
                feed = feedparser.parse(raw)
            except Exception as e:
                log.debug("rss parse %s failed: %s", rss_url, e)
                return
            for entry in (feed.entries or [])[:200]:
                eid = entry.get("id") or entry.get("guid") or entry.get("link")
                if not eid:
                    continue
                title = entry.get("title") or ""
                if needle and needle not in title.lower():
                    continue
                yield (
                    f"rss:{name}:{eid}",
                    {
                        "id": str(eid)[:300],
                        "title": title,
                        "url": entry.get("link") or "",
                        "feed": name,
                        "published": entry.get("published") or entry.get("updated") or "",
                        "summary": (entry.get("summary") or "")[:500],
                    },
                )

    _Rss.__name__ = f"Rss_{_safe_name(name)}"
    _Rss.interval = interval
    _Rss.category = category
    _Rss.display = display or name
    return _Rss


# ────────────────────────────────────────────────────────────────────────────
# Web JSON list endpoint
# ────────────────────────────────────────────────────────────────────────────

def make_web_json(
    url: str,
    name: str,
    *,
    display: Optional[str] = None,
    category: str = "web",
    interval: float = 1800.0,
    list_path: List[str] = (),
    id_field: str = "id",
    columns: Optional[List[str]] = None,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    transform: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Type[BaseSource]:
    src_name = f"web_{_safe_name(name)}"
    cols = list(columns or ["id", "title", "url"])
    _cat = category
    _disp = display or name

    class _WebJson(BaseSource):
        name = src_name
        category = _cat
        display = _disp
        interval = 1800.0
        columns = cols

        async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
            try:
                data = await self.http.get_json(url, headers=headers, params=params)
            except Exception as e:
                log.debug("web_json %s failed: %s", name, e)
                return
            cur = data
            for k in list_path:
                cur = (cur or {}).get(k, [])
            if not isinstance(cur, list):
                return
            for item in cur:
                if not isinstance(item, dict):
                    continue
                row = transform(item) if transform else item
                rid = row.get(id_field) or row.get("id") or row.get("url")
                if not rid:
                    continue
                yield (f"{name}:{rid}", {c: row.get(c, "") for c in cols})

    _WebJson.__name__ = f"WebJson_{_safe_name(name)}"
    _WebJson.interval = interval
    _WebJson.category = category
    _WebJson.display = display or name
    return _WebJson
