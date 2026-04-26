"""Runtime configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    """Global config, populated from env."""

    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
    admin_tg_id: int = field(default_factory=lambda: _int("ADMIN_TG_ID", 0))
    port: int = field(default_factory=lambda: _int("PORT", 10000))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    http_concurrency: int = field(default_factory=lambda: _int("HTTP_CONCURRENCY", 12))
    http_rps: float = field(default_factory=lambda: float(os.getenv("HTTP_RPS", "8") or 8))
    http_timeout: int = field(default_factory=lambda: _int("HTTP_TIMEOUT", 25))
    http_retries: int = field(default_factory=lambda: _int("HTTP_RETRIES", 3))
    user_agent: str = field(
        default_factory=lambda: os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        )
    )
    output_dir: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "runs")).resolve())
    public_url: str = field(default_factory=lambda: os.getenv("PUBLIC_URL", "").strip())


CONFIG = Config()
