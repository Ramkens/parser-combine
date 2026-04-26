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
        # stagger first ticks across ~300s to avoid thundering herd at startup
        stagger = (hash(src) & 0xFFFF) / 0xFFFF * 300.0
        try:
            await asyncio.wait_for(self._stop.wait(), timeout=stagger)
            return
        except asyncio.TimeoutError:
            pass
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
        """Compact summary fitting in a Telegram message."""
        lines = []
        if self.running:
            uptime = int(time.time() - (self._started_at or time.time()))
            state = "⏸ пауза" if self.paused else "идёт парсинг"
            lines.append(f"🟢 Запущен. Аптайм: <b>{uptime}s</b>. Состояние: <b>{state}</b>.")
        else:
            lines.append("⚪️ Остановлен.")

        total_items = self.store.total()
        n_sources = len(REGISTRY)
        active = sum(1 for s in self.store.sources.values() if s.total_seen > 0)
        ticked = sum(1 for s in self.state.values() if s.ticks > 0)
        errs = sum(1 for s in self.state.values() if s.last_error)
        lines.append(
            f"Источников: <b>{n_sources}</b> | с данными: <b>{active}</b> | "
            f"тикнули: <b>{ticked}</b> | ошибок: <b>{errs}</b>"
        )
        lines.append(f"Всего собрано: <b>{total_items}</b>")

        # ── По категориям (топ 15)
        by_cat: Dict[str, int] = {}
        for src, store in self.store.sources.items():
            cat = getattr(REGISTRY[src], "category", "misc")
            by_cat[cat] = by_cat.get(cat, 0) + store.total_seen
        if by_cat:
            lines.append("\n<b>По категориям (топ 15):</b>")
            for cat, n in sorted(by_cat.items(), key=lambda x: -x[1])[:15]:
                if n == 0:
                    continue
                lines.append(f"  • {cat}: <code>{n}</code>")

        # ── Топ источников
        ranked = sorted(
            self.store.sources.items(),
            key=lambda kv: -kv[1].total_seen,
        )[:15]
        if ranked and ranked[0][1].total_seen > 0:
            lines.append("\n<b>Топ источников:</b>")
            for src, store in ranked:
                if store.total_seen == 0:
                    continue
                cls = REGISTRY[src]
                lines.append(
                    f"  • <b>{(cls.display or src)[:40]}</b>: <code>{store.total_seen}</code>"
                )

        lines.append("\n<i>Команды:</i> /sources [n] — список (по 30), /cat &lt;name&gt; — фильтр")
        return "\n".join(lines)

    def sources_page(self, page: int = 1, per_page: int = 30, category: Optional[str] = None) -> str:
        """Paginated listing of all (or category-filtered) sources."""
        items = list(self.store.sources.items())
        if category:
            items = [(s, st) for s, st in items if getattr(REGISTRY[s], "category", "") == category]
        items.sort(key=lambda kv: (-kv[1].total_seen, kv[0]))
        total = len(items)
        if total == 0:
            return "Нет источников по этому фильтру."
        page = max(1, page)
        n_pages = (total + per_page - 1) // per_page
        page = min(page, n_pages)
        chunk = items[(page - 1) * per_page : page * per_page]

        header = f"<b>Источники {(page - 1) * per_page + 1}–{(page - 1) * per_page + len(chunk)}</b> из <b>{total}</b>"
        if category:
            header += f" (категория <b>{category}</b>)"
        header += f" • стр. <b>{page}/{n_pages}</b>"
        lines = [header, ""]
        for src, store in chunk:
            cls = REGISTRY[src]
            st = self.state.get(src) or SourceState()
            ago = int(time.time() - st.last_tick_at) if st.last_tick_at else None
            ago_s = f"{ago}s" if ago is not None else "—"
            err = " ⚠️" if st.last_error else ""
            lines.append(
                f"<code>{store.total_seen:>5}</code>  {(cls.display or src)[:42]}  "
                f"({getattr(cls, 'category', '')}) • last {ago_s}{err}"
            )
        if n_pages > 1:
            lines.append(f"\n<i>След.: /sources {min(page+1, n_pages)}; пред.: /sources {max(1, page-1)}</i>")
        return "\n".join(lines)

    def category_summary(self) -> str:
        """Returns one-message-fitting list of all categories with totals."""
        by_cat: Dict[str, list[int]] = {}
        for src, store in self.store.sources.items():
            cat = getattr(REGISTRY[src], "category", "misc")
            slot = by_cat.setdefault(cat, [0, 0])
            slot[0] += 1
            slot[1] += store.total_seen
        if not by_cat:
            return "Нет категорий."
        lines = [f"<b>Категорий:</b> {len(by_cat)}", ""]
        for cat, (n, items) in sorted(by_cat.items(), key=lambda x: -x[1][1]):
            lines.append(f"  • <b>{cat}</b> — источников <code>{n}</code>, items <code>{items}</code>")
        lines.append("\n<i>Фильтр: /cat &lt;name&gt;</i>")
        return "\n".join(lines)
