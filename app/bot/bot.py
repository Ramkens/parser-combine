"""Telegram bot built on aiogram v3 with admin-only access.

Flow:
  /start -> welcome + show menu
  /sources -> inline keyboard to toggle parser sources
  /keywords <csv> -> set keywords
  /limit <n> -> set per-source limit
  /run -> start a job in background, stream progress, attach ZIP+XLSX on finish
  /status -> show current selection / running job
  /cancel -> cancel running job
"""
from __future__ import annotations

import asyncio
import html
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.core.config import CONFIG
from app.core.logger import get_logger
from app.orchestrator import run_parse, RunResult
from app.parsers.registry import DISPLAY, REGISTRY, all_keys

log = get_logger("bot")


@dataclass
class UserState:
    sources: Set[str] = field(default_factory=lambda: {"wildberries", "steam", "habr"})
    keywords: List[str] = field(default_factory=list)
    limit: int = 50
    running_task: Optional[asyncio.Task] = None
    cancel_event: Optional[asyncio.Event] = None


_STATES: Dict[int, UserState] = {}


def _state(user_id: int) -> UserState:
    if user_id not in _STATES:
        _STATES[user_id] = UserState()
    return _STATES[user_id]


def _is_admin(user_id: int) -> bool:
    return CONFIG.admin_tg_id == 0 or user_id == CONFIG.admin_tg_id


def _sources_kb(selected: Set[str]) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    keys = all_keys()
    for i in range(0, len(keys), 2):
        row = []
        for k in keys[i:i + 2]:
            mark = "✅" if k in selected else "▫️"
            row.append(InlineKeyboardButton(text=f"{mark} {DISPLAY[k]}", callback_data=f"src:{k}"))
        rows.append(row)
    rows.append([
        InlineKeyboardButton(text="✅ Все", callback_data="src:_all"),
        InlineKeyboardButton(text="❌ Очистить", callback_data="src:_none"),
    ])
    rows.append([InlineKeyboardButton(text="🚀 Запустить", callback_data="src:_run")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


HELP_TEXT = (
    "<b>parser-combine</b>\n\n"
    "Команды:\n"
    "<code>/sources</code> — выбрать источники (галочки)\n"
    "<code>/keywords слово1, слово2</code> — задать ключевые слова\n"
    "<code>/limit 100</code> — лимит записей на источник\n"
    "<code>/run</code> — запустить парсинг\n"
    "<code>/status</code> — показать настройки и статус\n"
    "<code>/cancel</code> — отменить текущий парсинг\n"
)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            await m.answer("⛔ Доступ запрещён.")
            return
        s = _state(m.from_user.id)
        await m.answer(
            HELP_TEXT
            + f"\nТекущие источники: <code>{', '.join(sorted(s.sources)) or '—'}</code>\n"
            + f"Ключевые слова: <code>{', '.join(s.keywords) or '—'}</code>\n"
            + f"Лимит: <code>{s.limit}</code>",
        )

    @dp.message(Command("help"))
    async def on_help(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await m.answer(HELP_TEXT)

    @dp.message(Command("sources"))
    async def on_sources(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        s = _state(m.from_user.id)
        await m.answer("Выберите источники:", reply_markup=_sources_kb(s.sources))

    @dp.message(Command("keywords"))
    async def on_keywords(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        s = _state(m.from_user.id)
        text = (m.text or "").split(maxsplit=1)
        if len(text) < 2:
            await m.answer("Использование: <code>/keywords слово1, слово2</code>")
            return
        s.keywords = [w.strip() for w in text[1].split(",") if w.strip()]
        await m.answer(f"Ключевые слова: <code>{html.escape(', '.join(s.keywords) or '—')}</code>")

    @dp.message(Command("limit"))
    async def on_limit(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        s = _state(m.from_user.id)
        text = (m.text or "").split(maxsplit=1)
        if len(text) < 2 or not text[1].strip().isdigit():
            await m.answer("Использование: <code>/limit 100</code>")
            return
        s.limit = max(1, min(2000, int(text[1].strip())))
        await m.answer(f"Лимит на источник: <code>{s.limit}</code>")

    @dp.message(Command("status"))
    async def on_status(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        s = _state(m.from_user.id)
        running = bool(s.running_task and not s.running_task.done())
        await m.answer(
            f"Источники: <code>{', '.join(sorted(s.sources)) or '—'}</code>\n"
            f"Ключевые слова: <code>{html.escape(', '.join(s.keywords) or '—')}</code>\n"
            f"Лимит: <code>{s.limit}</code>\n"
            f"Запущено: <code>{'да' if running else 'нет'}</code>",
        )

    @dp.message(Command("cancel"))
    async def on_cancel(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        s = _state(m.from_user.id)
        if s.running_task and not s.running_task.done():
            s.running_task.cancel()
            await m.answer("⏹ Отмена запрошена.")
        else:
            await m.answer("Нечего отменять.")

    @dp.message(Command("run"))
    async def on_run(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await _kickoff_run(m)

    @dp.callback_query(F.data.startswith("src:"))
    async def on_src(cb: CallbackQuery) -> None:
        if not _is_admin(cb.from_user.id):
            await cb.answer("⛔", show_alert=False)
            return
        s = _state(cb.from_user.id)
        action = cb.data.split(":", 1)[1]
        if action == "_all":
            s.sources = set(all_keys())
        elif action == "_none":
            s.sources = set()
        elif action == "_run":
            await cb.answer("Запускаю…")
            await _kickoff_run(cb.message, user_id=cb.from_user.id)
            return
        elif action in REGISTRY:
            if action in s.sources:
                s.sources.discard(action)
            else:
                s.sources.add(action)
        await cb.message.edit_reply_markup(reply_markup=_sources_kb(s.sources))
        await cb.answer()

    return dp


async def _kickoff_run(m: Message, user_id: Optional[int] = None) -> None:
    uid = user_id or m.from_user.id
    s = _state(uid)
    if s.running_task and not s.running_task.done():
        await m.answer("Уже идёт парсинг. <code>/cancel</code> чтобы отменить.")
        return
    if not s.sources:
        await m.answer("Не выбраны источники. /sources")
        return
    progress_msg = await m.answer(
        f"🚀 Запускаю парсинг: <code>{', '.join(sorted(s.sources))}</code>\n"
        f"Ключевые слова: <code>{html.escape(', '.join(s.keywords) or '—')}</code>\n"
        f"Лимит: <code>{s.limit}</code>"
    )

    counts: Dict[str, int] = {k: 0 for k in s.sources}
    last_edit = [0.0]

    async def progress(src: str, cur: int, _total: int) -> None:
        counts[src] = cur
        # throttle edits to avoid 429s
        import time as _t
        now = _t.monotonic()
        if now - last_edit[0] < 2.0:
            return
        last_edit[0] = now
        try:
            text = "📊 Прогресс:\n" + "\n".join(
                f"  • {DISPLAY.get(k, k)}: <b>{v}</b>" for k, v in counts.items()
            )
            await progress_msg.edit_text(text)
        except Exception:
            pass

    bot: Bot = m.bot

    async def runner() -> None:
        try:
            res: RunResult = await run_parse(
                sorted(s.sources), s.keywords, limit_per_source=s.limit, progress=progress
            )
            summary = (
                f"✅ Готово за {res.duration:.1f}s\n"
                f"Найдено: <b>{sum(res.counts.values())}</b>\n"
                + "\n".join(f"  • {DISPLAY.get(k, k)}: <b>{v}</b>" for k, v in res.counts.items())
            )
            if res.errors:
                summary += "\n\n⚠️ Ошибки:\n" + "\n".join(
                    f"  • {DISPLAY.get(k, k)}: {html.escape(v)[:120]}" for k, v in res.errors.items()
                )
            await m.answer(summary)
            if res.zip_path and res.zip_path.exists():
                await bot.send_document(
                    chat_id=m.chat.id,
                    document=FSInputFile(str(res.zip_path), filename=f"{res.run_id}.zip"),
                )
            if res.xlsx_path and res.xlsx_path.exists():
                await bot.send_document(
                    chat_id=m.chat.id,
                    document=FSInputFile(str(res.xlsx_path), filename=f"{res.run_id}.xlsx"),
                )
        except asyncio.CancelledError:
            await m.answer("⏹ Отменено.")
            raise
        except Exception as e:
            log.exception("run failed")
            await m.answer(f"❌ Ошибка: <code>{html.escape(str(e))[:300]}</code>")

    s.running_task = asyncio.create_task(runner())


async def start_bot() -> tuple[Bot, asyncio.Task]:
    if not CONFIG.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    bot = Bot(
        token=CONFIG.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()
    log.info("bot polling starting (admin=%s)", CONFIG.admin_tg_id)
    task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    return bot, task
