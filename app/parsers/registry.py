"""Discover all parsers and expose a name -> class registry."""
from __future__ import annotations

from typing import Dict, Type

from app.parsers.base import BaseParser
from app.parsers.telegram_web import TelegramWebParser
from app.parsers.twogis import TwoGISParser
from app.parsers.lolz import LolzParser
from app.parsers.steam import SteamParser
from app.parsers.wildberries import WildberriesParser
from app.parsers.hh import HHParser
from app.parsers.habr import HabrParser
from app.parsers.reddit import RedditParser
from app.parsers.hackernews import HackerNewsParser
from app.parsers.github_trending import GitHubTrendingParser
from app.parsers.pikabu import PikabuParser
from app.parsers.avito import AvitoParser
from app.parsers.vk import VKParser

REGISTRY: Dict[str, Type[BaseParser]] = {
    "telegram": TelegramWebParser,
    "2gis": TwoGISParser,
    "lolz": LolzParser,
    "steam": SteamParser,
    "wildberries": WildberriesParser,
    "hh": HHParser,
    "habr": HabrParser,
    "reddit": RedditParser,
    "hackernews": HackerNewsParser,
    "github": GitHubTrendingParser,
    "pikabu": PikabuParser,
    "avito": AvitoParser,
    "vk": VKParser,
}

# Display names for UI
DISPLAY = {
    "telegram": "Telegram (web)",
    "2gis": "2GIS",
    "lolz": "Lolz.live",
    "steam": "Steam (free)",
    "wildberries": "Wildberries (cheap)",
    "hh": "HeadHunter",
    "habr": "Habr",
    "reddit": "Reddit",
    "hackernews": "Hacker News",
    "github": "GitHub Trending",
    "pikabu": "Pikabu",
    "avito": "Avito",
    "vk": "VK (web)",
}


def all_keys() -> list[str]:
    return list(REGISTRY.keys())
