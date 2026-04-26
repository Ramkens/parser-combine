"""Telegram public channels via t.me/s/<channel>.

Each entry: (channel_username, category). Channels that 404 just stay
empty — the harvester logs a debug message and moves on.
"""
from __future__ import annotations

CHANNELS_BY_CATEGORY: dict[str, list[str]] = {
    "tg-halyava": [
        "halyavshchik", "gohalyava", "halyava_news", "halyavshikiii",
        "halyava_msk", "halyava_spb", "halyava_zone", "halyavablog",
        "halyavyplus", "halyavadlyavseh", "kuponomania", "kupon_promo",
        "promokod_skidka", "kupony_skidki", "freebie_ru",
        "halyavaru", "besplatno_msk", "besplatno_spb", "sharasanya",
        "sharavpodarok", "halyavafromlife", "halyava_blog",
        "deshman_msk", "deshman_spb", "halyava_internet",
        "halyava_today", "halyava_kupony", "halyava_skidki",
        "halyava_official", "khalyava", "halyavshik",
        "freegamesbot", "freegamesnews", "deshevishe_chat",
        "skidki_promokody", "promokody_skidki", "skidochki_chat",
        "deals_chat", "promo_kanal", "kuponchik_skidki",
        "halyavyzona", "halyava_24", "halyava_777",
        "halyava_promo", "halyava_chat_msk", "halyava_chat_spb",
        "halyava_top", "halyava_chat", "halyava_news_chat",
        "halyavsky", "halyavtut", "halyavus_chat",
        "halyavchikru", "halyavadarom", "halyavarom",
        "halyavnik", "halyavshchikspb", "halyavshchikmsk",
        "kuponii", "kuponhalyava", "kuponomaniachat",
        "promokodimsk", "promokodi_chat", "promokoda",
        "promokod_chat", "promokod_msk", "promokod_spb",
        "promokod_ru", "promokod_skidki_kupon",
        "halyava_24_7", "halyava_otzovik", "halyava_xochu",
    ],
    "tg-deals": [
        "ozonskidki", "ozon_skidki_promo", "wb_skidki_promokody",
        "wb_promo_skidki", "yandex_market_promo", "aliexpress_skidki",
        "ali_promokody", "skidki_aliexpress", "letyshops_news",
        "kupon_promo_kod", "skidkadnya", "skidki_dnya_chat",
        "deal_hunters", "smart_deal_ru", "promogrosh",
        "promostore_ru", "skidka_promo", "promokod_otziv",
        "ozon_max_skidka", "wb_max_skidka", "yandex_skidka",
        "lamoda_skidki", "alibaba_skidki", "ebay_skidki",
        "amazon_skidki_ru", "deals_today_ru", "skidki_aliexpress_chat",
        "ozon_chat", "wb_chat", "yandex_chat",
        "deals_msk", "deals_spb", "deals_kazan",
        "deals_novosib", "deals_eburg",
        "ozonprosto", "wb_prosto", "ozon_promo",
        "wb_promo", "wb_skidkidnya",
    ],
    "tg-books": [
        "knigi_audio", "knigi_besplatno", "knigi_skachat",
        "free_books_ru", "knigi_pdf", "audioknigi_besplatno",
        "knigi_xochu", "biblioteka_kniga", "freebooks_pdf",
        "kniga_chat", "klassika_knigi", "litres_share",
        "litres_promo", "audible_share", "audible_promo",
        "knigichat", "knigotwo", "knigochat",
        "litres_chat", "knigi_litres", "knigi_litres_chat",
        "kindle_share_ru", "ebook_share_ru", "scribd_share_ru",
        "knigobonus", "biblioteka_2050", "freekniga",
        "knigi_skidki", "knigi_chat_msk", "knigi_chat_spb",
    ],
    "tg-music": [
        "yandex_plus_share", "yaplus_promo", "spotify_share_ru",
        "youtube_premium_share", "muzika_besplatno", "music_free_ru",
        "music_promo", "musik_promokody", "yamuzyka_chat",
        "deezer_share", "tidal_share", "musicpromo_chat",
        "yandex_plus_chat", "yandex_music_chat",
        "spotify_chat_ru", "ytm_chat", "ytm_premium_share",
    ],
    "tg-vpn": [
        "free_vpn_ru", "vpn_promo", "vpn_skidki",
        "vpn_share_ru", "vpn_unlim", "vpn_freekeys",
        "outline_vpn_ru", "wireguard_vpn", "vpn_chat_official",
        "vpn_msk", "vpn_spb", "vpn_chat_ru",
        "freevpn_keys", "vpn_unlim_share", "vpnpromochat",
        "vpn_kupon", "vpn_promokod",
    ],
    "tg-courses": [
        "udemy_kupony", "udemy_skidki_ru", "free_courses_ru",
        "skillbox_skidki", "stepik_skidki", "free_education_ru",
        "kursy_besplatno", "kursy_chat", "udemy_free_ru",
        "skillbox_promo", "geekbrains_promo", "yandex_practicum_promo",
        "netology_promo", "stepik_promo", "udemy_chat_ru",
        "coursera_chat_ru", "edx_chat_ru", "freecodecamp_ru",
        "freelearning_ru", "kursy_msk", "kursy_spb",
        "kursy_xochu", "udemy_share_chat",
    ],
    "tg-giveaway": [
        "giveaways_steam", "free_steam_keys", "free_games_steam_ru",
        "epic_free_games", "freebies_games", "free_keys_chat",
        "stim_keys_free", "playmarket_keys", "appstore_keys",
        "rewards_chat", "key_giveaway", "key_drop_chat",
        "steam_keys_giveaway", "epic_keys_giveaway",
        "gog_keys_giveaway", "humble_keys_chat",
        "giveaway_steam_ru", "key_chat_ru",
        "free_steam_games_chat", "epic_games_chat_ru",
    ],
    "tg-cashback": [
        "cashback_help", "cashback_chat", "letyshops",
        "epn_cashback", "rakuten_ru", "kapus_ru",
        "letyshop_chat", "megabonus_chat", "cashback_promo",
        "cashback_chat_msk", "cashback_chat_spb",
    ],
    "tg-apps": [
        "appshopper_free_ru", "androidapps_free", "appstore_free_apps",
        "free_apps_today", "ios_apps_free", "google_play_free",
        "softfreebies", "free_software_ru", "android_free_ru",
        "ios_free_ru", "free_apps_share", "android_apk_free",
        "appsfree_chat", "ios_freebies_chat", "play_store_share",
    ],
    "tg-crypto": [
        "crypto_airdrop_ru", "airdrops_chat", "free_crypto_ru",
        "airdrops_alert", "airdrop_chat_ru", "freeairdrops_chat",
        "airdrop_msk", "airdrop_spb", "crypto_promo_ru",
        "free_btc_ru", "free_eth_ru", "free_token_ru",
        "airdrop_news_ru", "airdrop_today",
    ],
    "tg-yandex": [
        "yandex_market_skidki", "yandex_lavka_promo",
        "yandex_uslugi_promo", "yandex_eda_promo", "yandex_taxi_promo",
        "yandex_plus_news", "yandex_kinopoisk_promo",
        "yandex_zen_promo", "yandex_practicum_promo",
        "yandex_market_chat", "yandex_lavka_chat",
        "yandex_eda_chat", "yandex_taxi_chat",
    ],
    "tg-foreign": [
        "freebies_uk", "freebies_us", "freebies_eu",
        "freebie_chat", "freebies_chat", "freebies_world",
        "freebies_canada", "freebies_australia",
        "freebies_germany", "freebies_france",
    ],
    "tg-food": [
        "halyava_food", "free_food_ru", "skidki_food_ru",
        "promo_food_ru", "yandex_eda_skidki", "delivery_club_promo",
    ],
    "tg-travel": [
        "halyava_travel", "skidki_travel_ru", "promo_travel_ru",
        "promo_aviabilet", "skidki_aviabilet",
        "kupon_travel_ru", "tripinsider_chat",
    ],
    "tg-news": [
        "halyava_news_ru", "promokod_news",
        "kupon_news", "skidki_news_chat",
    ],
}

# Flatten
CHANNELS = []
_seen = set()
for cat, lst in CHANNELS_BY_CATEGORY.items():
    for ch in lst:
        if ch.lower() in _seen:
            continue
        _seen.add(ch.lower())
        CHANNELS.append((ch, cat))
