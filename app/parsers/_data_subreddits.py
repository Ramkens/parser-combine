"""Big static list of subreddits to harvest, by category.

Each entry: (subreddit_name, category, optional title-filter substring).
The harvester keeps a separate dedupe state per subreddit. Subs that
return 403/404 simply stay empty without breaking the run.
"""
from __future__ import annotations
from typing import List, Optional, Tuple

# (subreddit, category, title_filter_or_None)
_GENERIC_FREEBIES = [
    "freebies", "FreeStuffOnTheInternet", "GoodfreeStuff", "FreeBoxes",
    "FreeStuff", "FreebieFinder", "FreebiesUS", "FreeUSA",
    "FreebieFinderUK", "Freebies_UK", "freebiesUK", "FreeStuffUK",
    "FreebiesAU", "freebiesAUS", "FreebiesCanada", "FreeCanada",
    "FreeIndia", "freebiesIndia", "FreeKarma4U", "FreeKarma",
    "Free_Karma_4_Karma", "FreeFlys", "FreeSamples", "FreebieFromHome",
    "FreeContent", "FreeStuff_NoSurveys", "freebiezzz", "FreebieFairy",
    "FreebieGroup", "FreebieFarm", "FreebieJunkie", "FreebieFanatic",
    "FreebieFinderUSA", "FreebieDailyFinds", "frugal", "frugalmalefashion",
    "ineedabudget", "GoFreebies", "extremecouponing", "couponing",
    "TheTextbookHub", "freebierecipes", "freebiesperu", "freebiesweden",
    "FreebieAlerts", "freebieapps", "freebiesforu", "freebie_offers",
    "FreebieDigest", "FreebieScout",
]

_FREE_GAMES = [
    "FreeGameFindings", "FreeGamesOnSteam", "FreeGamesFinders",
    "RandomActsOfGaming", "GiftofGames", "FreeAccounts",
    "FreeGamesForAll", "FreeIndieGames", "GameDealsMeta",
    "ItchIoFreebies", "FreeKey", "FreeKeysGames", "FreeGameKeys",
    "FreeKeyTrade", "freegamesofficial", "AppHookup",
    "AppStoreDeals", "AppStoreFreeApps", "PaidAppsBlackList",
    "AndroidApps", "AndroidFreebies", "AndroidGameDeals",
    "AndroidGaming", "MobileGameDeals", "MobileGameFreebies",
    "PSPlus", "PSPlusGames", "PlayStationPlus", "XboxGamePass",
    "XboxLiveGoldDeals", "XboxOneDeals", "NintendoSwitchDeals",
    "SwitchEshopDeals", "GiveAwayBots", "FreeIndieGameKeys",
    "EpicFreeGames", "EpicGamesFreebies", "Steam", "EpicGamesPC",
    "GogDealsTrack", "GogDeals", "ItchIo", "ItchIoFreeKeys",
    "FreeAccountsHub", "GiveawayHub", "GameTrade", "GameSwap",
    "MobileGiveaways", "freegamechat", "FreeOnSteam",
    "PaidGamesGoneFree", "freegameaday", "RandomActsofGames",
    "AndroidGamingFreebies", "iosGamingFreebies",
    "FreeAndroidApps", "AppStoreFree", "FreebieAppCanada",
    "OpenSourceGameDev", "FreeWeb3Games",
]

_GAME_DEALS_FREE_ONLY = [
    # sub will only keep posts whose title includes "free"
    "GameDeals", "GameDealsCanada", "GameDealsMeta", "GameDealsUK",
    "PCGamingDeals", "ConsoleDeals", "PCGameDealsHumor",
    "Gaming_Deals_Daily", "EpicGamesPC", "EpicFreeGames",
    "GogDeals", "GogDealsTrack", "ItchIo", "tabletopgamedeals",
    "ConsoleDealsCanada", "GamingMemes", "PSDeals", "XboxDeals",
    "SwitchDeals", "PSPlusDeals", "GamePassDeals",
    "RoyalRumbleDeals", "OriginDeals", "NintendoSwitchDeals",
]

_COUPONS = [
    "coupons", "freecoupons", "couponswap", "CouponDealsCanada",
    "AmazonCoupons", "couponsonline", "couponcommunity",
    "couponswithoutsignin", "FreeFlys", "frugalfemalefashion",
    "PromoCodes", "promo", "promocodes_4u", "discounts",
    "shoppingdeals", "DealMakers", "BlackFridayDeals",
    "DealsOnTheGo", "WeeklyDeals", "RetailMeNotDeals",
    "HoneyDeals", "RakutenDeals", "ebatesdeals",
    "ExtremeCouponingTip", "CouponersUnited", "CouponHaul",
    "couponbug", "PromoCodeShare", "DiscountCodes",
    "DealCommunity", "OnlineCouponingTeam", "DealsByTheDay",
    "couponsuitable", "GroceryCoupons", "CrazyCouponing",
    "CouponThis", "Couponswithoutsignin", "redditdeals",
    "SaveTheBacon",
]

_BOOKS = [
    "freeebooks", "FreeEBOOKS", "kindlefreebies", "KindleDeals",
    "ebookdeals", "ebookpaid", "BookGiveaways", "FreeAudiobookCodes",
    "AudiobookDeals", "audiobooks", "BookDealsCanada",
    "BookDeals", "BookDealsAU", "BookDealsUK", "FreeBookOffers",
    "ProjectGutenberg", "FreeBooks", "FreeIndieBooks",
    "FreeAudioBookCodes", "AudibleHandouts", "FreeAudible",
    "AudibleDeals", "EbookCommunity", "Indieebooks",
    "FreeFiction", "freenovels", "freeitbookz", "ScribdShare",
    "OpenLibrary", "FreebieBookworm", "freekindlebooks",
    "freenookbooks", "freekoboBooks", "freebooksnz",
    "Indie_AudiobookGiveaway", "DigitalBookFreebies",
    "kindlescoutsuccess", "FreeNovellas", "WattpadFreebies",
]

_COURSES = [
    "udemyfreebies", "UdemyFreebiesGenerator", "UdemyDealsForYou",
    "FreeOnlineCourses", "FreeUdemyCoupons", "Free_Online_Courses",
    "freecodecamp", "FreeCertifications", "OnlineLearning",
    "edX", "MOOC", "coursera", "OpenCourses", "AcademicEbooks",
    "FreeCourseCanada", "DataIsBeautiful", "learnprogramming",
    "Python_Free_Courses", "FreeProgramming", "javascript",
    "css", "webdev", "datascience_free_courses",
    "FreeMOOCs", "MoocCommunity", "OpenCoursesShare",
    "Khanacademy", "Coursera_Free", "FreeUdemyCourses",
    "edx_free_courses", "PluralsightFreeWeek", "freelancersclub",
    "freelearning", "freelearningstuff", "freedevcourse",
]

_VPN = [
    "VPN", "VPNDeals", "VPNTorrents", "Cloudflare",
    "PrivacyGuides", "ProtonVPN", "Mullvad", "windscribe",
    "AtlasVPN", "vpncoupons", "freevpns", "vpnpromos",
    "VpnDealsAndCoupons", "PrivacyToolsIO", "PrivacyTipsForUs",
    "VPNRecommendations", "VPNReviews", "ProxyDeals",
    "FreeProxy", "OpenVPN", "wireguard", "FreeWireguard",
    "FreeShadowsocks", "FreeXrayVPN",
]

_MUSIC_FREE = [
    "freemusic", "freemusicpromos", "spotifypremium",
    "SpotifyDeals", "youtubepremium", "YouTubeMusic",
    "AppleMusic", "MusicForFree", "freemusicarchive",
    "BandcampDaily", "newAlbumReleases", "MusicPromosTracker",
    "deezerpremium", "tidalpremium", "musicfreebies",
    "Audius", "FreeFLACs", "openmusic", "creativecommonsmusic",
    "FreeMusicSamples", "FreeMusicLoops",
]

_RU = [
    "yandex", "YandexPlus", "russia", "RussianDeals",
    "russiandevs", "Pikabu", "AskARussian", "rusAskReddit",
    "halyavchik", "PromoRussia", "skidkiRu", "kuponiRu",
]

_REWARDS = [
    "beermoney", "beermoneyglobal", "signupsforpay",
    "GoodOfflineSurveys", "PaidOnlineSurveys", "passive_income",
    "sweepstakes", "Sweepstakes_Pro", "SweepstakesContests",
    "rewardsapps", "FreeSamples", "samplesharer",
    "MicroEarn", "PassiveIncomeApps", "BeerMoneyAdvice",
    "ContestSweepstakes", "Sweeptakes", "SweepsAndContests",
    "RealLifeSweepstakes", "EveryFreebie",
    "FreebiesAdvice", "FreebieJunkies",
]

_DESIGN = [
    "FreeAssets", "freegfx", "GFX_Freebies",
    "blenderhelp", "freecadweekly", "FreeArtAndDesign",
    "FreeDesignAssets", "graphic_design", "BlenderShare",
    "OpenSourceMusic", "OpenSourceArt", "OpenAssets",
    "freelancegigs", "FreeIcons", "FreeFonts", "FreePhotos",
    "creativecommons",
]

_CRYPTO = [
    "CryptoAirdrops", "Airdrop", "ethdev", "CryptoMoonShots",
    "CryptoCurrencyTrading", "FreeCoins", "FreeBitcoin",
    "AirdropsBros", "BountyHunter", "CryptoBountys",
    "CryptoFaucets", "FaucetCommunity",
]

_FOOD = [
    "FoodFreebies", "FreeFood", "FreebiesAtTheStore",
    "FreeFoodCanada", "FreeStuffFood", "DiningSweepstakes",
]

_STREAMING = [
    "freeIPTV", "Cordcutters", "StreamingDeals",
    "PlexFreeTrials", "FreeMovies", "FreeMoviesOnline",
    "MovieDealsAndOffers", "PrimeFreebies",
]

_LOCAL_US = [
    "FreeStuffNYC", "FreeStuffLA", "FreeStuffSeattle",
    "FreeStuffPortland", "FreeStuffChicago", "FreeStuffBoston",
    "FreeStuffMiami", "FreeStuffDenver", "FreeStuffPhoenix",
    "FreeStuffDallas", "FreeStuffHouston", "FreeStuffAtlanta",
    "FreeStuffOrlando", "freestuffSF", "freestuffSD",
    "FreeStuffOC", "FreeStuffNJ", "FreeStuffWA",
    "FreeStuffMD", "FreeStuffPA", "FreeStuffVA",
    "FreeStuffTX", "FreeStuffNC", "FreeStuffMI",
    "FreeStuffMN", "FreeStuffIN", "FreeStuffOH",
    "FreeStuffIL", "FreeStuffWI", "FreeStuffMA",
    "FreeStuffNV", "FreeStuffAZ", "FreeStuffCO",
    "FreeStuffOR", "FreeStuffID", "FreeStuffUT",
    "FreebiesNYC", "FreebiesLA", "FreebiesChicago",
    "FreebiesSeattle", "FreebiesAustin", "FreebiesPDX",
    "FreebiesDallas", "FreebiesNoVA",
]

_WORLD_DEALS = [
    "ukfree", "australian_freebies", "FreebiesNZ",
    "FreebieGermany", "FreebiesFrance", "FreebiesItaly",
    "FreebiesSpain", "FreebiesPoland", "FreebiesBrasil",
    "FreebiesMexico", "FreebiesArgentina", "FreebiesIreland",
    "FreebiesScotland", "FreebiesEngland",
    "FreebiesAustria", "FreebiesPortugal", "FreebiesGreece",
    "FreebiesNetherlands", "FreebiesBelgium", "FreebiesDenmark",
    "FreebiesSweden", "FreebiesNorway", "FreebiesFinland",
    "FreebiesSwitzerland", "FreebiesCzech", "FreebiesSlovak",
    "FreebiesHungary", "FreebiesRomania", "FreebiesBulgaria",
    "FreebiesUkraine", "FreebiesLatvia", "FreebiesLithuania",
    "FreebiesEstonia", "FreebiesTurkey", "FreebiesIsrael",
    "FreebiesEgypt", "FreebiesUAE", "FreebiesSaudi",
    "FreebiesPakistan", "FreebiesBangladesh", "FreebiesPhilippines",
    "FreebiesMalaysia", "FreebiesSingapore", "FreebiesThailand",
    "FreebiesIndonesia", "FreebiesVietnam", "FreebiesJapan",
    "FreebiesKorea", "FreebiesTaiwan", "FreebiesHongKong",
    "FreebiesChina", "FreebiesSouthAfrica", "FreebiesNigeria",
    "FreebiesKenya",
]

_HW_DEALS = [
    # Hardware / electronics deal subreddits where free or near-free leaks
    "buildapcsales", "buildapcsalescanada", "buildapcsalesuk",
    "buildapcsalesgermany", "buildapcsalesindia", "buildapcsalesAU",
    "MechanicalKeyboardDeals", "headphoneDeals", "audiophilemarket",
    "MonitorDeals", "GPUDeals", "CPUDeals", "RAMDeals",
    "SSDDeals", "HDDeals", "TVDeals", "TabletDeals",
    "PhoneDeals", "WatchDeals", "CameraDeals",
    "PrinterDeals", "RouterDeals",
]

_SOFTWARE = [
    "softwaredeals", "freeware", "OpenSource",
    "AppHookup", "softwaregore", "free_software",
    "windowsapps", "macapps", "linuxapps",
    "softwarefreebies", "appsharing",
    "appsdeals", "freebieapps",
]

_PRINT_FREE = [
    # 3D printing / makers free models
    "3Dprinting", "3DPrintingDeals", "3Dmodel",
    "FreeSTL", "Free3DPrints", "OpenSourceModels",
    "blender", "3DGiveaways",
]

_TRAVEL = [
    "travel_freebies", "TravelHacks", "TravelDeals",
    "PointsAndTravel", "AwardTravel", "travel_promos",
    "TravelSweepstakes", "FreeTravel", "BackpackingDeals",
    "FlyerDealsAndOffers", "FreeFlights", "FreeMiles",
]

_GAMING_PER_PLATFORM = [
    # Per-platform freebie tracker subs
    "PSN", "PSNDeals", "EAPlay", "OriginDeals",
    "StreamingTV", "FreeChannelGames", "FreeAppleArcade",
    "FreeAppStoreOnly", "FreeStadia", "FreeLuna",
    "FreeShadow", "FreeGeforceNow", "PlayStationDealsCanada",
    "XboxDealsCanada", "NintendoDealsCanada",
]

_FAMILY_FREEBIES = [
    "BabyFreebies", "FreeKidsStuff", "FreeForToddlers",
    "FreeBabyStuff", "BabyFreebieFinder", "MomsFreebies",
    "PetFreebies", "FreeDogStuff", "FreeCatStuff",
    "FreeBibsCoupons",
]

_CRAFTS_AND_DIY = [
    "freeCrafts", "freecrochetpatterns", "freepatterns",
    "freeknittingpatterns", "freeembroideryDesigns",
    "freecutfiles", "freescrapbook", "FreeQuilting",
]

_FITNESS_FREEBIES = [
    "freefitness", "freeworkouts", "FreeYogaClasses",
    "FitnessApps", "freegymsessions", "FreePilates",
]

# ─────────────────────────────────────────────────────────────────────────────
SUBREDDITS: List[Tuple[str, str, Optional[str]]] = []

for s in _GENERIC_FREEBIES:
    SUBREDDITS.append((s, "freebies", None))
for s in _FREE_GAMES:
    SUBREDDITS.append((s, "free-games", None))
for s in _GAME_DEALS_FREE_ONLY:
    SUBREDDITS.append((s, "game-deals", "free"))
for s in _COUPONS:
    SUBREDDITS.append((s, "coupons", None))
for s in _BOOKS:
    SUBREDDITS.append((s, "books", None))
for s in _COURSES:
    SUBREDDITS.append((s, "courses", None))
for s in _VPN:
    SUBREDDITS.append((s, "vpn", None))
for s in _MUSIC_FREE:
    SUBREDDITS.append((s, "music-free", None))
for s in _RU:
    SUBREDDITS.append((s, "ru", None))
for s in _REWARDS:
    SUBREDDITS.append((s, "rewards", None))
for s in _DESIGN:
    SUBREDDITS.append((s, "design", None))
for s in _CRYPTO:
    SUBREDDITS.append((s, "crypto-airdrops", None))
for s in _FOOD:
    SUBREDDITS.append((s, "food", None))
for s in _STREAMING:
    SUBREDDITS.append((s, "streaming", None))
for s in _LOCAL_US:
    SUBREDDITS.append((s, "local-us", None))
for s in _WORLD_DEALS:
    SUBREDDITS.append((s, "world", None))
for s in _HW_DEALS:
    SUBREDDITS.append((s, "hw-deals", "free"))
for s in _SOFTWARE:
    SUBREDDITS.append((s, "software", None))
for s in _PRINT_FREE:
    SUBREDDITS.append((s, "3d-print", None))
for s in _TRAVEL:
    SUBREDDITS.append((s, "travel", None))
for s in _GAMING_PER_PLATFORM:
    SUBREDDITS.append((s, "platform-deals", "free"))
for s in _FAMILY_FREEBIES:
    SUBREDDITS.append((s, "family", None))
for s in _CRAFTS_AND_DIY:
    SUBREDDITS.append((s, "crafts", None))
for s in _FITNESS_FREEBIES:
    SUBREDDITS.append((s, "fitness", None))

# Deduplicate by subreddit name (case-insensitive).
_seen: set = set()
_uniq: List[Tuple[str, str, Optional[str]]] = []
for sub, cat, flt in SUBREDDITS:
    key = sub.lower()
    if key in _seen:
        continue
    _seen.add(key)
    _uniq.append((sub, cat, flt))
SUBREDDITS = _uniq
