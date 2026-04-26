"""Infinite harvester loop.

Each registered source is run on its own schedule. New rows (by stable id)
are appended to the per-source store. The loop respects pause/resume and
shuts down cleanly.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from app.core.config import CONFIG
from app.core.http import HttpClient
from app.core.logger import get_logger
from app.parsers.registry import REGISTRY
from app.store import Store

log = get_logger("harvester")


@dataclass
class SourceState:
    last_tick_at: float = 0.0
    last_tick_added: int = 0
    last_tick_dur: float = 0.0
    last_error: str = ""
    ticks: int = 0


class Harvester:
    def __init__(self) -> None:
        self.data_dir = (CONFIG.output_dir / "data").resolve()
        self.store = Store(
            self.data_dir,
            sources={src: list(cls.columns) for src, cls in REGISTRY.items()},
        )
        self.state: Dict[str, SourceState] = {src: SourceState() for src in REGISTRY}
        self._paused = asyncio.Event()
        self._paused.set()  # not paused initially
        self._stop = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
        self._http: Optional[HttpClient] = None
        self._started_at: Optional[float] = None

    @property
    def running(self) -> bool:
        return bool(self._tasks) and any(not t.done() for t in self._tasks)

    @property
    def paused(self) -> bool:
        return not self._paused.is_set()

    @property
    def started_at(self) -> Optional[float]:
        return self._started_at

    async def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._paused.set()
        self._http = await HttpClient().__aenter__()
        self._started_at = time.time()
        for src in REGISTRY:
            self._tasks.append(asyncio.create_task(self._run_source(src), name=f"src-{src}"))
        log.info("harvester started: %s sources", len(self._tasks))

    async def stop(self) -> None:
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        if self._http is not None:
            try:
                await self._http.__aexit__(None, None, None)
            finally:
                self._http = None
        log.info("harvester stopped")

    def pause(self) -> None:
        self._paused.clear()

    def resume(self) -> None:
        self._paused.set()

    def reset_all(self) -> None:
        self.store.reset_all()
        for s in self.state.values():
            s.ticks = 0
            s.last_tick_added = 0

    async def _run_source(self, src: str) -> None:
        cls = REGISTRY[src]
        source = cls(self._http)
        store = self.store.get(src)
        st = self.state[src]
        # stagger first ticks slightly to avoid simultaneous bursts
        await asyncio.sleep(min(2.0, hash(src) % 5))
        while not self._stop.is_set():
            await self._paused.wait()  # wait if paused
            tick_started = time.time()
            added = 0
            try:
                async for item_id, row in source.tick():
                    if self._stop.is_set():
                        break
                    if store.add(item_id, row):
                        added += 1
                st.last_error = ""
            except asyncio.CancelledError:
                raise
            except Exception as e:
                st.last_error = f"{type(e).__name__}: {e}"
                log.warning("[%s] tick failed: %s", src, e)
            st.last_tick_at = tick_started
            st.last_tick_added = added
            st.last_tick_dur = time.time() - tick_started
            st.ticks += 1
            log.info("[%s] tick #%s: +%s items in %.1fs (total=%s)",
                     src, st.ticks, added, st.last_tick_dur, store.total_seen)
            # sleep until next interval, but stay responsive to stop
            interval = float(getattr(cls, "interval", 600.0))
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=interval)
                break  # stop signalled
            except asyncio.TimeoutError:
                pass

    def status_text(self) -> str:
        lines = []
        if self.running:
            uptime = int(time.time() - (self._started_at or time.time()))
            lines.append(f"🟢 Запущен. Аптайм: <b>{uptime}s</b>. Состояние: <b>{'⏸ пауза' if self.paused else 'идёт парсинг'}</b>.")
        else:
            lines.append("⚪️ Остановлен.")
        lines.append(f"Всего собрано: <b>{self.store.total()}</b>")
        for src, store in self.store.sources.items():
            cls = REGISTRY[src]
            st = self.state.get(src) or SourceState()
            last = "—"
            if st.last_tick_at:
                ago = int(time.time() - st.last_tick_at)
                last = f"{ago}s назад, +{st.last_tick_added}"
            lines.append(
                f"  • <b>{cls.display or src}</b>: total <code>{store.total_seen}</code>, "
                f"new(сесс) <code>{store.new_added}</code>, last: {last}"
            )
            if st.last_error:
                lines.append(f"     ⚠️ <code>{st.last_error[:100]}</code>")
        return "\n".join(lines)
