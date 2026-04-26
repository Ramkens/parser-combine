"""Programmatically-generated source lists.

These builders produce thousands of distinct RSS/web endpoints by combining
search queries, languages, categories, etc. The output is a list of
(name, url, category, title_filter, display) tuples in the same shape as
`_data_rss.RSS_FEEDS`.
"""
from __future__ import annotations

import urllib.parse
from typing import List, Tuple

Feed = Tuple[str, str, str, object, str]  # (name, url, category, filter, display)


# ─── Big keyword pools ─────────────────────────────────────────────────────

# Topics for "free <X>" queries
GENERIC_FREE_TOPICS = [
    # games / gaming
    "game", "games", "steam game", "epic game", "indie game", "mobile game",
    "PC game", "playstation game", "xbox game", "nintendo switch game",
    "roblox", "fortnite", "minecraft", "VR game",
    # books & media
    "ebook", "ebooks", "audiobook", "audiobooks", "kindle", "comic", "comics",
    "manga", "novel", "textbook", "magazine", "newspaper",
    # courses / learning
    "course", "courses", "udemy course", "coursera course", "edX course",
    "tutorial", "bootcamp", "training", "certification", "MOOC",
    # software / apps
    "software", "app", "apps", "iOS app", "Android app", "chrome extension",
    "VPN", "antivirus", "firewall", "office suite", "PDF tool",
    # subscriptions / streaming
    "subscription", "trial", "Netflix trial", "Spotify trial", "Disney trial",
    "Amazon Prime trial", "YouTube Premium trial", "Apple Music trial",
    "HBO trial", "ChatGPT", "Claude", "Midjourney",
    # design / creative assets
    "font", "fonts", "icon", "icons", "stock photo", "stock video", "vector",
    "mockup", "Lightroom preset", "Photoshop action", "after effects template",
    # web / cloud / dev
    "domain", "web hosting", "VPS", "cloud credit", "AWS credit",
    "GitHub student pack", "API key", "SSL certificate",
    # crypto / airdrop
    "airdrop", "crypto airdrop", "NFT mint", "faucet", "testnet token",
    # life / household
    "sample", "samples", "coupon", "coupons", "voucher", "rebate",
    "gift card", "amazon gift card", "shipping", "trial pack",
    # food / drink
    "coffee", "pizza sample", "snack sample", "cocktail recipe",
    # travel
    "flight voucher", "hotel night", "travel credit", "airline miles",
    # health / fitness
    "workout plan", "yoga class", "meal plan", "vitamins sample",
    # kids / family
    "kids book", "homework help", "online classroom",
    # music / audio
    "music download", "royalty-free music", "sample pack", "VST plugin",
    # productivity / business
    "Notion template", "Excel template", "Google docs template",
    "resume template", "invoice template",
]

RU_FREE_TOPICS = [
    "бесплатно игра", "бесплатно курс", "бесплатно книга", "бесплатно ВПН",
    "промокод яндекс", "промокод озон", "промокод вб", "промокод delivery",
    "промокод тинькофф", "халява", "розыгрыш", "раздача", "акция кэшбэк",
    "бесплатная подписка", "бесплатный пробный период", "бесплатное обучение",
    "бесплатные шрифты", "бесплатные иконки", "бесплатные шаблоны",
    "промокод ozon", "промокод wildberries", "халява игра",
    "халява стим", "халява epic", "халява steam ключ",
]

# Themes (topic, search-query) pairs for Reddit search
REDDIT_KEYWORDS = [
    "free", "free game", "free games", "free key", "free ebook", "free course",
    "freebie", "giveaway", "trial", "promo code", "100% off",
    "free credits", "free vpn", "free subscription", "free shipping",
    "free coupon", "voucher", "free sample", "free font", "free icon",
]

# arXiv top-level categories: cs.AI, cs.CL, cs.LG, math.ST, etc. We'll list
# the popular subject classes.
ARXIV_CATEGORIES = [
    # CS
    "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV",
    "cs.CY", "cs.DB", "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL",
    "cs.GL", "cs.GR", "cs.GT", "cs.HC", "cs.IR", "cs.IT", "cs.LG", "cs.LO",
    "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI", "cs.OH", "cs.OS",
    "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY",
    # Math
    "math.AC", "math.AG", "math.AP", "math.AT", "math.CA", "math.CO",
    "math.CT", "math.CV", "math.DG", "math.DS", "math.FA", "math.GM",
    "math.GN", "math.GR", "math.GT", "math.HO", "math.IT", "math.KT",
    "math.LO", "math.MG", "math.MP", "math.NA", "math.NT", "math.OA",
    "math.OC", "math.PR", "math.QA", "math.RA", "math.RT", "math.SG",
    "math.SP", "math.ST",
    # Stat / Q-Bio / Q-Fin / Econ
    "stat.AP", "stat.CO", "stat.ME", "stat.ML", "stat.OT", "stat.TH",
    "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT",
    "q-bio.PE", "q-bio.QM", "q-bio.SC", "q-bio.TO",
    "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR",
    "q-fin.RM", "q-fin.ST", "q-fin.TR",
    "econ.EM", "econ.GN", "econ.TH",
    # Physics / astro
    "astro-ph.CO", "astro-ph.EP", "astro-ph.GA", "astro-ph.HE",
    "astro-ph.IM", "astro-ph.SR",
    "cond-mat.dis-nn", "cond-mat.mes-hall", "cond-mat.mtrl-sci",
    "cond-mat.other", "cond-mat.quant-gas", "cond-mat.soft",
    "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con",
    "physics.acc-ph", "physics.ao-ph", "physics.app-ph", "physics.atm-clus",
    "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
    "physics.comp-ph", "physics.data-an", "physics.ed-ph", "physics.flu-dyn",
    "physics.gen-ph", "physics.geo-ph", "physics.hist-ph", "physics.ins-det",
    "physics.med-ph", "physics.optics", "physics.plasm-ph", "physics.pop-ph",
    "physics.soc-ph", "physics.space-ph",
    "hep-ex", "hep-lat", "hep-ph", "hep-th", "gr-qc", "nucl-ex", "nucl-th",
    "math-ph", "nlin.AO", "nlin.CD", "nlin.CG", "nlin.PS", "nlin.SI",
    "quant-ph",
]

# Google News languages × regions
GNEWS_LANGS: List[Tuple[str, str]] = [
    ("en-US", "US:en"), ("en-GB", "GB:en"), ("en-CA", "CA:en"),
    ("en-AU", "AU:en"), ("en-IN", "IN:en"),
    ("ru-RU", "RU:ru"), ("uk-UA", "UA:uk"),
    ("de-DE", "DE:de"), ("fr-FR", "FR:fr"), ("es-ES", "ES:es"),
    ("it-IT", "IT:it"), ("pl-PL", "PL:pl"), ("pt-BR", "BR:pt-419"),
    ("tr-TR", "TR:tr"), ("ja-JP", "JP:ja"), ("ko-KR", "KR:ko"),
    ("zh-CN", "CN:zh-Hans"),
]

# Mastodon instances we know expose public hashtag RSS at
# https://<instance>/tags/<tag>.rss
MASTODON_INSTANCES = [
    "mastodon.social", "mastodon.online", "mas.to", "fosstodon.org",
    "techhub.social", "infosec.exchange", "hachyderm.io", "sigmoid.social",
    "indieweb.social", "freeradical.zone", "deals.rss", "social.linux.pizza",
    "kolektiva.social", "mstdn.party", "mastodon.world", "mstdn.social",
]
MASTODON_HASHTAGS = [
    "free", "freebie", "freebies", "giveaway", "deals", "freegames",
    "freebook", "freeebook", "freecourse", "humblebundle", "epicgames",
    "steam", "gog", "indiegame", "bundle", "halyava", "promocode",
    "discount", "sale", "bargain", "cashback", "gratis", "kostenlos",
    "gratuit", "darmowe",
]


# ─── Builders ──────────────────────────────────────────────────────────────


def _q(s: str) -> str:
    return urllib.parse.quote_plus(s)


def hn_algolia_feeds() -> List[Feed]:
    """HN Algolia search RSS for many free-topic queries."""
    out: List[Feed] = []
    for kw in GENERIC_FREE_TOPICS:
        q = f"free {kw}"
        url = f"https://hnrss.org/newest?q={_q(q)}"
        out.append((
            f"hn_{q}",
            url,
            "hn-search",
            None,
            f"HN search: {q}",
        ))
    return out


def google_news_feeds() -> List[Feed]:
    """Google News RSS for free-topic queries across many languages."""
    out: List[Feed] = []
    for hl, ceid in GNEWS_LANGS:
        topics = GENERIC_FREE_TOPICS if hl.startswith(("en", "de", "fr", "es", "it", "pl", "pt", "tr", "ja", "ko", "zh")) else GENERIC_FREE_TOPICS
        if hl.startswith("ru"):
            topics = RU_FREE_TOPICS
        for kw in topics:
            q = kw if hl.startswith("ru") else f"free {kw}"
            url = (
                f"https://news.google.com/rss/search?q={_q(q)}"
                f"&hl={hl}&gl={hl.split('-')[1]}&ceid={ceid}"
            )
            out.append((
                f"gnews_{hl}_{q}",
                url,
                f"gnews-{hl}",
                None,
                f"Google News {hl}: {q}",
            ))
    return out


def reddit_search_feeds() -> List[Feed]:
    """Reddit search RSS for many free-related queries."""
    out: List[Feed] = []
    for kw in REDDIT_KEYWORDS:
        for topic in GENERIC_FREE_TOPICS:
            q = f"{kw} {topic}"
            url = f"https://www.reddit.com/search.rss?q={_q(q)}&sort=new&restrict_sr=off"
            out.append((
                f"redditsr_{q}",
                url,
                "reddit-search",
                None,
                f"Reddit search: {q}",
            ))
    return out


def arxiv_feeds() -> List[Feed]:
    """arXiv per-category RSS (open-access papers)."""
    out: List[Feed] = []
    for cat in ARXIV_CATEGORIES:
        out.append((
            f"arxiv_{cat.replace('-', '_').replace('.', '_')}",
            f"http://export.arxiv.org/rss/{cat}",
            "arxiv",
            None,
            f"arXiv {cat}",
        ))
    return out


def mastodon_feeds() -> List[Feed]:
    out: List[Feed] = []
    for inst in MASTODON_INSTANCES:
        for tag in MASTODON_HASHTAGS:
            out.append((
                f"mast_{inst.replace('.', '_')}_{tag}",
                f"https://{inst}/tags/{tag}.rss",
                "mastodon",
                None,
                f"Mastodon {inst} #{tag}",
            ))
    return out


def all_generated() -> List[Feed]:
    feeds: List[Feed] = []
    feeds += hn_algolia_feeds()
    feeds += google_news_feeds()
    feeds += reddit_search_feeds()
    feeds += arxiv_feeds()
    feeds += mastodon_feeds()
    # Dedup by URL
    seen = set()
    out: List[Feed] = []
    for f in feeds:
        url = f[1]
        if url in seen:
            continue
        seen.add(url)
        out.append(f)
    return out
