"""Shared aiohttp client with retry + rate limiting."""
from __future__ import annotations

import asyncio
import random
from typing import Any, Optional

import aiohttp

from app.core.config import CONFIG
from app.core.logger import get_logger
from app.core.ratelimit import Limiter

log = get_logger("http")


class HttpClient:
    """Thin wrapper around aiohttp.ClientSession with retries and rate limiting."""

    def __init__(self, limiter: Optional[Limiter] = None) -> None:
        self._limiter = limiter or Limiter(CONFIG.http_concurrency, CONFIG.http_rps)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "HttpClient":
        timeout = aiohttp.ClientTimeout(total=CONFIG.http_timeout)
        connector = aiohttp.TCPConnector(limit=CONFIG.http_concurrency * 2, ttl_dns_cache=300)
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": CONFIG.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Upgrade-Insecure-Requests": "1",
            },
            trust_env=True,
        )
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("HttpClient not entered")
        return self._session

    async def request(
        self,
        method: str,
        url: str,
        *,
        as_json: bool = False,
        **kwargs: Any,
    ) -> Any:
        last_exc: Optional[BaseException] = None
        for attempt in range(1, CONFIG.http_retries + 1):
            try:
                async with self._limiter.slot():
                    async with self.session.request(method, url, **kwargs) as resp:
                        if resp.status in (429, 500, 502, 503, 504):
                            raise aiohttp.ClientResponseError(
                                resp.request_info, resp.history, status=resp.status,
                                message=f"retryable status {resp.status}",
                            )
                        resp.raise_for_status()
                        if as_json:
                            return await resp.json(content_type=None)
                        return await resp.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exc = e
                if attempt == CONFIG.http_retries:
                    log.warning("GET %s failed after %s tries: %s", url, attempt, e)
                    raise
                delay = min(8.0, 0.6 * (2 ** (attempt - 1))) + random.random() * 0.4
                log.debug("retry %s/%s for %s in %.1fs (%s)", attempt, CONFIG.http_retries, url, delay, e)
                await asyncio.sleep(delay)
        if last_exc:
            raise last_exc
        raise RuntimeError("unreachable")

    async def get(self, url: str, **kwargs: Any) -> str:
        return await self.request("GET", url, as_json=False, **kwargs)

    async def get_json(self, url: str, **kwargs: Any) -> Any:
        return await self.request("GET", url, as_json=True, **kwargs)
