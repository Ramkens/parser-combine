"""Source registry."""
from __future__ import annotations

from typing import Dict, Type

from app.parsers.base import BaseSource
from app.parsers.steam_free import SteamFreeSource
from app.parsers.roblox_free import RobloxFreeSource
from app.parsers.epic_free import EpicFreeSource
from app.parsers.gog_free import GogFreeSource
from app.parsers.itchio_free import ItchIoFreeSource
from app.parsers.freetogame import FreeToGameSource
from app.parsers.gamerpower import GamerPowerSource
from app.parsers.reddit_free import RedditFreeSource

REGISTRY: Dict[str, Type[BaseSource]] = {
    "steam": SteamFreeSource,
    "roblox": RobloxFreeSource,
    "epic": EpicFreeSource,
    "gog": GogFreeSource,
    "itchio": ItchIoFreeSource,
    "freetogame": FreeToGameSource,
    "gamerpower": GamerPowerSource,
    "reddit": RedditFreeSource,
}


def all_keys() -> list[str]:
    return list(REGISTRY.keys())
