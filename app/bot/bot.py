"""Telegram bot for the infinite free-stuff harvester."""
from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.core.config import CONFIG
from app.core.logger import get_logger
from app.harvester import Harvester
from app.output.packer import build_snapshot
from app.parsers.registry import REGISTRY

log = get_logger("bot")


HELP_TEXT = (
    "<b>parser-combine — бесконечный парсер бесплатного</b>\n\n"
    "Команды:\n"
    "<code>/start</code> — запустить парсинг (если не запущен) + статус\n"
    "<code>/status</code> — статус и счётчики\n"
    "<code>/stop</code> — остановить (полностью)\n"
    "<code>/pause</code> — пауза\n"
    "<code>/resume</code> — продолжить\n"
    "<code>/download</code> — получить снимок (ZIP + XLSX) прямо сейчас\n"
    "<code>/reset</code> — обнулить всю собранную базу\n"
)


def _is_admin(user_id: int) -> bool:
    return CONFIG.admin_tg_id == 0 or user_id == CONFIG.admin_tg_id


def _main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статус", callback_data="cmd:status"),
            InlineKeyboardButton(text="📥 Скачать", callback_data="cmd:download"),
        ],
        [
            InlineKeyboardButton(text="⏸ Пауза", callback_data="cmd:pause"),
            InlineKeyboardButton(text="▶️ Продолжить", callback_data="cmd:resume"),
        ],
        [
            InlineKeyboardButton(text="⏹ Стоп", callback_data="cmd:stop"),
            InlineKeyboardButton(text="🗑 Сброс", callback_data="cmd:reset"),
        ],
    ])


def build_dispatcher(harvester: Harvester) -> Dispatcher:
    dp = Dispatcher()
    snapshots_dir = (CONFIG.output_dir / "snapshots").resolve()

    async def deny(m: Message) -> None:
        await m.answer("⛔ Доступ запрещён.")

    @dp.message(CommandStart())
    async def on_start(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return await deny(m)
        if not harvester.running:
            await harvester.start()
        await m.answer(HELP_TEXT, reply_markup=_main_kb())
        await m.answer(harvester.status_text(), reply_markup=_main_kb())

    @dp.message(Command("help"))
    async def on_help(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await m.answer(HELP_TEXT, reply_markup=_main_kb())

    @dp.message(Command("status"))
    async def on_status(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await m.answer(harvester.status_text(), reply_markup=_main_kb())

    @dp.message(Command("stop"))
    async def on_stop(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await harvester.stop()
        await m.answer("⏹ Остановлен.", reply_markup=_main_kb())

    @dp.message(Command("pause"))
    async def on_pause(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        harvester.pause()
        await m.answer("⏸ Пауза.", reply_markup=_main_kb())

    @dp.message(Command("resume"))
    async def on_resume(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        if not harvester.running:
            await harvester.start()
        harvester.resume()
        await m.answer("▶️ Продолжаю.", reply_markup=_main_kb())

    @dp.message(Command("reset"))
    async def on_reset(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        harvester.reset_all()
        await m.answer("🗑 База обнулена.", reply_markup=_main_kb())

    @dp.message(Command("download"))
    async def on_download(m: Message) -> None:
        if not _is_admin(m.from_user.id):
            return
        await _send_snapshot(m, harvester, snapshots_dir)

    @dp.callback_query(F.data.startswith("cmd:"))
    async def on_cb(cb: CallbackQuery) -> None:
        if not _is_admin(cb.from_user.id):
            await cb.answer("⛔", show_alert=False)
            return
        action = cb.data.split(":", 1)[1]
        if action == "status":
            await cb.message.answer(harvester.status_text(), reply_markup=_main_kb())
        elif action == "pause":
            harvester.pause()
            await cb.message.answer("⏸ Пауза.", reply_markup=_main_kb())
        elif action == "resume":
            if not harvester.running:
                await harvester.start()
            harvester.resume()
            await cb.message.answer("▶️ Продолжаю.", reply_markup=_main_kb())
        elif action == "stop":
            await harvester.stop()
            await cb.message.answer("⏹ Остановлен.", reply_markup=_main_kb())
        elif action == "reset":
            harvester.reset_all()
            await cb.message.answer("🗑 База обнулена.", reply_markup=_main_kb())
        elif action == "download":
            await _send_snapshot(cb.message, harvester, snapshots_dir)
        await cb.answer()

    return dp


async def _send_snapshot(m: Message, harvester: Harvester, snapshots_dir: Path) -> None:
    notice = await m.answer("📦 Собираю снимок (ZIP + XLSX)…")
    try:
        sources = {src: list(cls.columns) for src, cls in REGISTRY.items()}
        # Run packer in default executor — it's I/O + CPU bound
        loop = asyncio.get_running_loop()
        zip_path, xlsx_path = await loop.run_in_executor(
            None,
            lambda: build_snapshot(harvester.data_dir, snapshots_dir, sources),
        )
        await m.bot.send_document(
            chat_id=m.chat.id,
            document=FSInputFile(str(zip_path), filename=zip_path.name),
            caption=f"ZIP: всего <b>{harvester.store.total()}</b> записей",
        )
        await m.bot.send_document(
            chat_id=m.chat.id,
            document=FSInputFile(str(xlsx_path), filename=xlsx_path.name),
            caption="Excel со всеми листами",
        )
        try:
            await notice.delete()
        except Exception:
            pass
    except Exception as e:
        log.exception("snapshot failed")
        await m.answer(f"❌ Ошибка снимка: <code>{e}</code>")


async def start_bot(harvester: Harvester) -> tuple[Bot, asyncio.Task]:
    if not CONFIG.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    bot = Bot(
        token=CONFIG.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher(harvester)
    log.info("bot polling starting (admin=%s)", CONFIG.admin_tg_id)
    task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    return bot, task
