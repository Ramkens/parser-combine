"""App entrypoint: aiohttp server (for Render keepalive) + Telegram bot polling."""
from __future__ import annotations

import asyncio
import signal

from app.bot.bot import start_bot
from app.core.config import CONFIG
from app.core.logger import get_logger, setup_logging
from app.server import start_server

log = get_logger("main")


async def amain() -> None:
    setup_logging()
    runner = await start_server()
    bot = None
    bot_task = None
    if CONFIG.telegram_bot_token:
        bot, bot_task = await start_bot()
    else:
        log.warning("TELEGRAM_BOT_TOKEN missing — bot disabled, only HTTP server runs")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _stop() -> None:
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            pass

    try:
        await stop.wait()
    finally:
        log.info("shutting down")
        if bot_task:
            bot_task.cancel()
            try:
                await bot_task
            except (asyncio.CancelledError, Exception):
                pass
        if bot:
            try:
                await bot.session.close()
            except Exception:
                pass
        await runner.cleanup()


def main() -> None:
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
