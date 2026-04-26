"""Source registry — dynamically built from factories + dedicated parsers."""
from __future__ import annotations

import random
from typing import Dict, Type

from app.parsers.base import BaseSource
from app.parsers.factories import make_reddit_sub, make_rss, make_tg_channel
from app.parsers._data_subreddits import SUBREDDITS
from app.parsers._data_telegram import CHANNELS
from app.parsers._data_rss import RSS_FEEDS

# Dedicated, hand-written parsers for richer extraction
from app.parsers.steam_free import SteamFreeSource
from app.parsers.roblox_free import RobloxFreeSource
from app.parsers.epic_free import EpicFreeSource
from app.parsers.gog_free import GogFreeSource
from app.parsers.itchio_free import ItchIoFreeSource
from app.parsers.freetogame import FreeToGameSource
from app.parsers.gamerpower import GamerPowerSource


REGISTRY: Dict[str, Type[BaseSource]] = {}


def _add(cls: Type[BaseSource]) -> None:
    if cls.name in REGISTRY:
        return
    REGISTRY[cls.name] = cls


# ── Dedicated rich parsers ─────────────────────────────────────────────────
SteamFreeSource.category = "free-games-api"
RobloxFreeSource.category = "free-games-api"
EpicFreeSource.category = "free-games-api"
GogFreeSource.category = "free-games-api"
ItchIoFreeSource.category = "free-games-api"
FreeToGameSource.category = "free-games-api"
GamerPowerSource.category = "free-games-api"
for c in (
    SteamFreeSource, RobloxFreeSource, EpicFreeSource, GogFreeSource,
    ItchIoFreeSource, FreeToGameSource, GamerPowerSource,
):
    _add(c)


# ── Reddit subreddits (factory) ────────────────────────────────────────────
_rng = random.Random(42)
for sub, cat, flt in SUBREDDITS:
    interval = 900.0 + _rng.uniform(-180.0, 600.0)  # 12–25 min
    cls = make_reddit_sub(sub, category=cat, interval=interval, title_must_match=flt)
    _add(cls)

# ── Telegram public channels (factory) ─────────────────────────────────────
for ch, cat in CHANNELS:
    interval = 1200.0 + _rng.uniform(-300.0, 900.0)  # 15–35 min
    cls = make_tg_channel(ch, category=cat, interval=interval)
    _add(cls)

# ── RSS / Atom feeds (factory) ─────────────────────────────────────────────
for name, url, cat, flt, display in RSS_FEEDS:
    interval = 1500.0 + _rng.uniform(-300.0, 1200.0)  # 20–45 min
    cls = make_rss(url, name, display=display, category=cat, interval=interval, title_must_match=flt)
    _add(cls)


def all_keys() -> list[str]:
    return list(REGISTRY.keys())


def by_category() -> Dict[str, list[str]]:
    out: Dict[str, list[str]] = {}
    for name, cls in REGISTRY.items():
        out.setdefault(getattr(cls, "category", "misc"), []).append(name)
    return out
