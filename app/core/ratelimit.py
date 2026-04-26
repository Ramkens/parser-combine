"""Async rate limiting primitives."""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator


class TokenBucket:
    """Simple async token bucket: `rps` tokens per second, capacity = rps."""

    def __init__(self, rps: float) -> None:
        self.rps = max(0.1, float(rps))
        self.capacity = max(1.0, self.rps)
        self._tokens = self.capacity
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, weight: float = 1.0) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rps)
                self._last = now
                if self._tokens >= weight:
                    self._tokens -= weight
                    return
                deficit = weight - self._tokens
                wait = deficit / self.rps
                await asyncio.sleep(wait)


class Limiter:
    """Concurrency cap + rate limit combined."""

    def __init__(self, concurrency: int, rps: float) -> None:
        self._sem = asyncio.Semaphore(max(1, int(concurrency)))
        self._bucket = TokenBucket(rps)

    @asynccontextmanager
    async def slot(self) -> AsyncIterator[None]:
        await self._bucket.acquire()
        async with self._sem:
            yield
