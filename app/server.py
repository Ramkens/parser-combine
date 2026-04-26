"""Tiny aiohttp keepalive server for Render free tier + cron-job.org pings."""
from __future__ import annotations

import time

from aiohttp import web

from app.core.config import CONFIG
from app.core.logger import get_logger

log = get_logger("server")

_STARTED = time.time()


async def handle_root(_: web.Request) -> web.Response:
    uptime = int(time.time() - _STARTED)
    return web.Response(text=f"parser-combine up. uptime={uptime}s")


async def handle_health(_: web.Request) -> web.Response:
    return web.json_response({"ok": True, "uptime": int(time.time() - _STARTED)})


async def handle_ping(_: web.Request) -> web.Response:
    return web.Response(text="pong")


def build_app() -> web.Application:
    app = web.Application()
    app.add_routes([
        web.get("/", handle_root),
        web.get("/healthz", handle_health),
        web.get("/ping", handle_ping),
    ])
    return app


async def start_server() -> web.AppRunner:
    app = build_app()
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=CONFIG.port)
    await site.start()
    log.info("HTTP server listening on :%s", CONFIG.port)
    return runner
