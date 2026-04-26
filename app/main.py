"""App entrypoint: HTTP keepalive server + Telegram bot + harvester."""
from __future__ import annotations

import asyncio
import signal

from app.bot.bot import start_bot
from app.core.config import CONFIG
from app.core.logger import get_logger, setup_logging
from app.harvester import Harvester
from app.server import start_server

log = get_logger("main")


async def amain() -> None:
    setup_logging()
    harvester = Harvester()
    await harvester.start()  # auto-start: harvest forever
    runner = await start_server()
    bot = None
    bot_task = None
    if CONFIG.telegram_bot_token:
        bot, bot_task = await start_bot(harvester)
    else:
        log.warning("TELEGRAM_BOT_TOKEN missing — bot disabled, only HTTP+harvester run")

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
        await harvester.stop()
        await runner.cleanup()


def main() -> None:
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
