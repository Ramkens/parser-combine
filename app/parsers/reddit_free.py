"""Reddit freebies subreddits via public .json endpoints."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Tuple

from app.core.logger import get_logger
from app.parsers.base import BaseSource

log = get_logger("src.reddit")


_SUBS = ["FreeGameFindings", "freebies", "GameDeals", "FreeGamesOnSteam"]


class RedditFreeSource(BaseSource):
    name = "reddit"
    display = "Reddit /r/FreeGameFindings + freebies + GameDeals"
    columns = ["id", "title", "url", "subreddit", "permalink", "author", "created"]
    interval = 300.0  # 5 min

    async def tick(self) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        for sub in _SUBS:
            after: str | None = None
            for _ in range(3):
                params: Dict[str, Any] = {"limit": 100, "raw_json": 1}
                if after:
                    params["after"] = after
                try:
                    data = await self.http.get_json(
                        f"https://www.reddit.com/r/{sub}/new.json",
                        params=params,
                        headers={"User-Agent": "parser-combine/1.0 (by u/anonymous)"},
                    )
                except Exception as e:
                    log.warning("reddit /r/%s failed: %s", sub, e)
                    break
                children = (data.get("data") or {}).get("children") or []
                if not children:
                    break
                for c in children:
                    d = c.get("data") or {}
                    pid = d.get("id")
                    if not pid:
                        continue
                    title = d.get("title") or ""
                    if sub.lower() == "gamedeals":
                        # only keep titles indicating free
                        if "free" not in title.lower() and "100%" not in title:
                            continue
                    yield (
                        f"reddit:{pid}",
                        {
                            "id": pid,
                            "title": title,
                            "url": d.get("url") or "",
                            "subreddit": sub,
                            "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                            "author": d.get("author") or "",
                            "created": d.get("created_utc") or "",
                        },
                    )
                after = (data.get("data") or {}).get("after")
                if not after:
                    break
