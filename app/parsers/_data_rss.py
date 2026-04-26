"""RSS / Atom feeds.

Each entry: (name, url, category, title-filter or None, display).
Feeds that 404 or change format simply produce 0 items per tick.
"""
from __future__ import annotations

# (name, url, category, title_filter, display)
RSS_FEEDS = [
    # ── Deal / freebie aggregators ────────────────────────────────────────
    ("slickdeals_frontpage", "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&rss=1", "deals", "free", "Slickdeals frontpage (free)"),
    ("slickdeals_freebies", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=9&rss=1", "deals", None, "Slickdeals freebies"),
    ("bensbargains_freebies", "https://bensbargains.com/c/free-after-rebate.atom", "deals", None, "Ben's Bargains freebies"),
    ("dealnews_freebies", "https://www.dealnews.com/c142/Computers/Software/?rss=1", "deals", "free", "DealNews software (free)"),
    ("woot_main", "https://www.woot.com/feed", "deals", None, "Woot"),
    ("ozbargain_freebies", "https://www.ozbargain.com.au/cat/freebies/feed", "deals", None, "OzBargain freebies"),
    ("hotukdeals_freebies", "https://www.hotukdeals.com/rss/freebies", "deals", None, "HotUKDeals freebies"),
    ("dealsea_main", "https://feeds.feedburner.com/Dealseacom", "deals", "free", "Dealsea (free)"),
    ("freecycle_meta", "https://www.freecycle.org/explore/feed.rss", "freebies", None, "Freecycle"),
    ("retailmenot", "https://feeds.feedburner.com/RetailmenotBlog", "deals", "free", "RetailMeNot blog (free)"),

    # ── Free game / game-deal feeds ───────────────────────────────────────
    ("epic_free_news", "https://www.epicgames.com/site/en-US/news.rss", "free-games", "free", "Epic news (free)"),
    ("steam_news_free", "https://store.steampowered.com/feeds/news/?cc=us&l=english", "free-games", "free", "Steam news (free)"),
    ("rps_free", "https://www.rockpapershotgun.com/feed/all", "free-games", "free", "Rock Paper Shotgun (free)"),
    ("pcgamer_free", "https://www.pcgamer.com/feeds/all", "free-games", "free", "PC Gamer (free)"),
    ("freetowin", "https://feeds.feedburner.com/FreeToPlayMmorpg", "free-games", None, "FreeToPlay MMORPG"),
    ("mmoby2", "https://feeds.feedburner.com/MmobombFeed", "free-games", "free", "MMO Bomb (free)"),
    ("indiegamebundles", "https://www.indiegamebundles.com/feed/", "free-games", None, "IndieGameBundles"),
    ("indiegala_showcase", "https://freebies.indiegala.com/feed/", "free-games", None, "IndieGala showcase"),
    ("alphabetagamer_free", "https://www.alphabetagamer.com/feed/", "free-games", "free", "Alphabetagamer (free)"),

    # ── Books (free / freebie) ────────────────────────────────────────────
    ("gutenberg_recent", "https://www.gutenberg.org/cache/epub/feeds/today.rss", "books", None, "Project Gutenberg today"),
    ("standardebooks", "https://standardebooks.org/feeds/rss/new-ebooks", "books", None, "Standard Ebooks"),
    ("manning_free", "https://freecontent.manning.com/feed/", "books", None, "Manning free content"),
    ("apress_free", "https://www.apress.com/us/freebooks/rss", "books", None, "Apress free"),
    ("ofreebook", "https://www.ofreebook.com/feed", "books", None, "OFreeBook"),
    ("freebookcentre", "https://www.freebookcentre.net/rss.xml", "books", None, "FreeBookCentre"),
    ("freecomputerbooks", "http://www.freecomputerbooks.com/rss.xml", "books", None, "FreeComputerBooks"),
    ("ebookhunter", "https://ebookhunter.io/feed/", "books", None, "eBookHunter"),
    ("librivox", "https://librivox.org/rss/latest_releases", "books", None, "LibriVox audiobooks"),

    # ── Free courses / learning ───────────────────────────────────────────
    ("classcentral_free", "https://www.classcentral.com/report/feed/", "courses", "free", "Class Central blog (free)"),
    ("freecodecamp", "https://www.freecodecamp.org/news/rss/", "courses", None, "freeCodeCamp news"),
    ("openculture", "https://www.openculture.com/feed", "courses", "free", "Open Culture (free)"),
    ("hackr_free", "https://hackr.io/blog/feed", "courses", "free", "Hackr.io blog (free)"),
    ("udemy_freebies_blog", "https://www.udemyfreebies.com/feed", "courses", None, "Udemy Freebies blog"),
    ("real_python_free", "https://realpython.com/atom.xml", "courses", "free", "Real Python (free)"),

    # ── Free music ────────────────────────────────────────────────────────
    ("freemusicarchive", "https://freemusicarchive.org/featured.atom", "music-free", None, "Free Music Archive"),
    ("ccmixter", "https://ccmixter.org/api?f=rss", "music-free", None, "ccMixter"),
    ("jamendo_releases", "https://www.jamendo.com/api/feed?type=newalbums&format=rss", "music-free", None, "Jamendo new"),
    ("bandcamp_daily", "https://daily.bandcamp.com/feed", "music-free", "free", "Bandcamp Daily (free)"),

    # ── Free design / stock assets ────────────────────────────────────────
    ("smashing_freebies", "https://www.smashingmagazine.com/category/freebies/feed/", "design", None, "Smashing freebies"),
    ("freepik_free", "https://www.freepik.com/feeds/free", "design", None, "Freepik free"),
    ("flaticon_free", "https://www.flaticon.com/feed/free", "design", None, "Flaticon free"),
    ("undraw", "https://undraw.co/feed.xml", "design", None, "unDraw"),

    # ── Free apps / mobile ────────────────────────────────────────────────
    ("apphookup", "https://www.reddit.com/r/AppHookup/.rss", "apps", None, "AppHookup RSS"),
    ("appsgonefree", "https://feeds.feedburner.com/AppsGoneFree", "apps", None, "AppsGoneFree"),

    # ── Tech blogs (Free filter) ──────────────────────────────────────────
    ("hn_free_algolia", "https://hnrss.org/newest?q=free", "tech-free", None, "HN newest with 'free'"),
    ("hn_giveaway", "https://hnrss.org/newest?q=giveaway", "tech-free", None, "HN giveaway"),
    ("lobsters_free", "https://lobste.rs/search.rss?q=free&what=stories&order=newest", "tech-free", None, "Lobsters free"),
    ("devto_free", "https://dev.to/feed/tag/free", "tech-free", None, "DEV.to #free"),
    ("producthunt_free", "https://www.producthunt.com/feed?category=undefined", "products", "free", "Product Hunt (free)"),

    # ── VPN deals ─────────────────────────────────────────────────────────
    ("vpn_news", "https://www.bestvpn.com/feed/", "vpn", "free", "BestVPN (free)"),
    ("vpnmentor_free", "https://www.vpnmentor.com/feed/", "vpn", "free", "VPN Mentor (free)"),

    # ── Crypto airdrops ───────────────────────────────────────────────────
    ("airdropalert", "https://airdropalert.com/feed", "crypto-airdrops", None, "Airdrop Alert"),
    ("airdropbob", "https://airdropbob.com/feed", "crypto-airdrops", None, "AirdropBob"),

    # ── Sweepstakes / contests ────────────────────────────────────────────
    ("sweepstakesinseattle", "https://sweepstakesinseattle.com/feed/", "rewards", None, "Sweepstakes in Seattle"),
    ("sweepstakesfanatics", "https://sweepstakesfanatics.com/feed/", "rewards", None, "Sweepstakes Fanatics"),

    # ── Foreign deal sites ────────────────────────────────────────────────
    ("dealabs", "https://www.dealabs.com/rss/freebies", "deals-fr", None, "Dealabs freebies (FR)"),
    ("mydealz_freebies", "https://www.mydealz.de/rss/gratis", "deals-de", None, "MyDealz Gratis (DE)"),
    ("chollometro", "https://www.chollometro.com/rss/freebies", "deals-es", None, "Chollometro gratis (ES)"),
    ("pepper_it", "https://www.pepper.it/rss/freebies", "deals-it", None, "Pepper.it gratis (IT)"),
    ("pepper_pl", "https://www.pepper.pl/rss/freebies", "deals-pl", None, "Pepper.pl gratis (PL)"),

    # ── Russian deal/halyava blogs ────────────────────────────────────────
    ("halyavabraza", "https://halyava.braza.fund/rss", "ru-deals", None, "Halyava Braza"),

    # ── Slickdeals categorized subforums ──────────────────────────────────
    ("slickdeals_computers", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=10&rss=1", "deals", None, "Slickdeals computers"),
    ("slickdeals_software", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=11&rss=1", "deals", None, "Slickdeals software"),
    ("slickdeals_food", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=14&rss=1", "deals", None, "Slickdeals food"),
    ("slickdeals_health", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=12&rss=1", "deals", None, "Slickdeals health"),
    ("slickdeals_travel", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=15&rss=1", "deals", None, "Slickdeals travel"),
    ("slickdeals_apparel", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=18&rss=1", "deals", None, "Slickdeals apparel"),
    ("slickdeals_home", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=22&rss=1", "deals", None, "Slickdeals home"),
    ("slickdeals_video_games", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=70&rss=1", "deals", "free", "Slickdeals video games (free)"),
    ("slickdeals_pets", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=72&rss=1", "deals", None, "Slickdeals pets"),
    ("slickdeals_baby", "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&forumid%5B%5D=73&rss=1", "deals", None, "Slickdeals baby"),

    # ── OzBargain category feeds ──────────────────────────────────────────
    ("ozbargain_food", "https://www.ozbargain.com.au/cat/food/feed", "deals", None, "OzBargain food"),
    ("ozbargain_books", "https://www.ozbargain.com.au/cat/books/feed", "deals", None, "OzBargain books"),
    ("ozbargain_games", "https://www.ozbargain.com.au/cat/computing/feed", "deals", "free", "OzBargain games (free)"),
    ("ozbargain_internet", "https://www.ozbargain.com.au/cat/internet/feed", "deals", None, "OzBargain internet"),
    ("ozbargain_apps", "https://www.ozbargain.com.au/cat/computing-software/feed", "deals", None, "OzBargain apps"),
    ("ozbargain_movies", "https://www.ozbargain.com.au/cat/entertainment/feed", "deals", None, "OzBargain movies"),

    # ── HotUKDeals subforum feeds ─────────────────────────────────────────
    ("hotukdeals_gaming", "https://www.hotukdeals.com/rss/tag/gaming", "deals", "free", "HotUKDeals gaming"),
    ("hotukdeals_books", "https://www.hotukdeals.com/rss/tag/books", "deals", None, "HotUKDeals books"),
    ("hotukdeals_apps", "https://www.hotukdeals.com/rss/tag/apps", "deals", None, "HotUKDeals apps"),
    ("hotukdeals_films", "https://www.hotukdeals.com/rss/tag/films", "deals", None, "HotUKDeals films"),
    ("hotukdeals_food", "https://www.hotukdeals.com/rss/tag/food", "deals", None, "HotUKDeals food"),

    # ── MyDealz / Pepper categories ───────────────────────────────────────
    ("mydealz_apps", "https://www.mydealz.de/rss/gruppe/apps-spiele", "deals-de", None, "MyDealz Apps & Games"),
    ("mydealz_buecher", "https://www.mydealz.de/rss/gruppe/buecher", "deals-de", None, "MyDealz Bücher"),
    ("mydealz_lebensmittel", "https://www.mydealz.de/rss/gruppe/lebensmittel-getraenke", "deals-de", None, "MyDealz Lebensmittel"),
    ("mydealz_streaming", "https://www.mydealz.de/rss/gruppe/streaming-musik", "deals-de", None, "MyDealz Streaming"),
    ("mydealz_internet", "https://www.mydealz.de/rss/gruppe/internet-tv-mobilfunk", "deals-de", None, "MyDealz Internet/TV"),
    ("dealabs_apps", "https://www.dealabs.com/rss/groupe/apps-jeux-mobile", "deals-fr", None, "Dealabs apps"),
    ("dealabs_livres", "https://www.dealabs.com/rss/groupe/livres", "deals-fr", None, "Dealabs livres"),
    ("dealabs_streaming", "https://www.dealabs.com/rss/groupe/musique-streaming", "deals-fr", None, "Dealabs streaming"),
    ("chollometro_apps", "https://www.chollometro.com/rss/grupo/aplicaciones-juegos-moviles", "deals-es", None, "Chollometro apps"),
    ("chollometro_libros", "https://www.chollometro.com/rss/grupo/libros", "deals-es", None, "Chollometro libros"),
    ("pepper_apps", "https://www.pepper.it/rss/gruppi/app-giochi-mobile", "deals-it", None, "Pepper apps"),

    # ── Free-edu / academic ──────────────────────────────────────────────
    ("openedu_news", "https://blog.coursera.org/feed/", "courses", "free", "Coursera blog (free)"),
    ("edx_blog_free", "https://blog.edx.org/feed/", "courses", "free", "edX blog (free)"),
    ("oerblog", "https://oer.education/feed/", "courses", None, "OER Education"),

    # ── Free books — niche ────────────────────────────────────────────────
    ("worldlibrary", "https://www.worldlibrary.org/feed.rss", "books", None, "World Library"),
    ("ebookmall_free", "https://www.ebookmall.com/free-ebooks.atom", "books", None, "eBookMall free"),
    ("hoopla_freebies", "https://www.hoopladigital.com/feed/free", "books", None, "Hoopla free"),
    ("dailylit", "https://www.dailylit.com/feed", "books", None, "DailyLit"),
    ("bookbub_free", "https://www.bookbub.com/featured-deals.rss", "books", "free", "BookBub featured"),

    # ── Free music — niche ────────────────────────────────────────────────
    ("incompetech", "https://incompetech.com/wordpress/feed/", "music-free", None, "Incompetech (Kevin Macleod)"),
    ("jamendo_topweek", "https://www.jamendo.com/api/feed?type=top&format=rss", "music-free", None, "Jamendo top"),

    # ── Free podcasts ─────────────────────────────────────────────────────
    ("podcastalley", "https://www.podcastalley.com/feed.atom", "podcasts", "free", "Podcast Alley"),

    # ── Open source / dev freebies ────────────────────────────────────────
    ("github_blog", "https://github.blog/feed/", "tech-free", "free", "GitHub blog (free)"),
    ("aws_free_tier_blog", "https://aws.amazon.com/blogs/aws/feed/", "tech-free", "free", "AWS blog (free tier)"),
    ("digitalocean_free_credits", "https://www.digitalocean.com/blog/feed/", "tech-free", "free", "DigitalOcean blog (free)"),
    ("cloudflare_blog", "https://blog.cloudflare.com/rss/", "tech-free", "free", "Cloudflare blog (free)"),

    # ── Indie giveaway sites ──────────────────────────────────────────────
    ("indieretronews_free", "https://www.indieretronews.com/feeds/posts/default", "free-games", "free", "IndieRetroNews (free)"),
    ("freeforminds", "https://www.freeforminds.com/feed/", "free-games", None, "FreeForMinds"),
    ("freegameblog", "https://www.freegameblog.com/feed", "free-games", None, "FreeGameBlog"),

    # ── HOSAS gaming news ────────────────────────────────────────────────
    ("eurogamer_free", "https://www.eurogamer.net/feed", "free-games", "free", "Eurogamer (free)"),
    ("destructoid_free", "https://www.destructoid.com/feed/", "free-games", "free", "Destructoid (free)"),
    ("gamingbolt_free", "https://gamingbolt.com/feed", "free-games", "free", "GamingBolt (free)"),
    ("polygon_free", "https://www.polygon.com/rss/index.xml", "free-games", "free", "Polygon (free)"),

    # ── Crypto airdrops ───────────────────────────────────────────────────
    ("dropstab_news", "https://dropstab.com/blog/feed", "crypto-airdrops", "airdrop", "DropsTab airdrops"),
    ("airdropking", "https://airdropking.io/feed/", "crypto-airdrops", None, "AirdropKing"),
    ("freerewards_io", "https://freerewards.io/feed/", "crypto-airdrops", None, "FreeRewards"),

    # ── Free design / icons / fonts ───────────────────────────────────────
    ("dailyfreepiks", "https://www.dailyfreepik.com/feed/", "design", None, "DailyFreepik"),
    ("freebiesbug", "https://freebiesbug.com/feed/", "design", None, "Freebiesbug"),
    ("freebiesgallery", "https://freebiesgallery.com/feed/", "design", None, "Freebiesgallery"),
    ("dribbblefreebies", "https://dribbble.com/tags/freebies/shots/popular.rss", "design", None, "Dribbble freebies"),
    ("freelogo_design", "https://www.freelogodesign.org/feed", "design", None, "Free Logo Design"),

    # ── Free fonts ────────────────────────────────────────────────────────
    ("dafont_top", "https://www.dafont.com/rss.xml", "fonts", None, "DaFont top"),
    ("fontspace", "https://www.fontspace.com/rss/recent.xml", "fonts", None, "FontSpace recent"),
    ("urbanfonts", "https://www.urbanfonts.com/free-fonts.rss", "fonts", None, "Urban Fonts free"),
    ("googlefonts_blog", "https://fonts.google.com/blog/feed", "fonts", None, "Google Fonts blog"),

    # ── Coupon sites ──────────────────────────────────────────────────────
    ("retailmenot_blog", "https://www.retailmenot.com/blog/feed/", "coupons", None, "RetailMeNot blog"),
    ("groupon_freebies", "https://www.groupon.com/local/free.atom", "coupons", None, "Groupon free local"),

    # ── Paid apps gone free / iOS ─────────────────────────────────────────
    ("dealisle_ios", "https://www.dealisle.com/ios.rss", "apps", None, "DealIsle iOS"),
    ("appsapk_free", "https://www.appsapk.com/feed/", "apps", None, "AppsAPK"),
    ("paidappsalert", "https://www.paidappsalert.com/feed", "apps", None, "PaidAppsAlert"),
    ("appodeal_free", "https://www.appodeal.com/blog/feed/", "apps", "free", "Appodeal blog (free)"),

    # ── Newsletters / digest ──────────────────────────────────────────────
    ("freecodecamp_news_main", "https://www.freecodecamp.org/news/feed/", "courses", None, "freeCodeCamp news"),
    ("hackernoon_free", "https://hackernoon.com/feed", "tech-free", "free", "HackerNoon (free)"),
    ("medium_freebies", "https://medium.com/feed/tag/freebies", "tech-free", None, "Medium #freebies"),
    ("medium_freegames", "https://medium.com/feed/tag/free-games", "free-games", None, "Medium #free-games"),
    ("medium_giveaways", "https://medium.com/feed/tag/giveaways", "free-games", None, "Medium #giveaways"),

    # ── Chrome / Browser extension giveaways ──────────────────────────────
    ("chromestory", "https://www.chromestory.com/feed/", "tech-free", "free", "Chromestory (free)"),

    # ── Software giveaways ────────────────────────────────────────────────
    ("giveawayoftheday", "https://www.giveawayoftheday.com/feed/", "software", None, "Giveaway of the Day"),
    ("sharewareonsale", "https://feeds.feedburner.com/SharewareOnSale", "software", None, "SharewareOnSale"),
    ("malavida_giveaway", "https://www.malavida.com/en/giveaway.rss", "software", None, "Malavida giveaway"),
    ("bitsdujour", "https://www.bitsdujour.com/feed/discounts.atom", "software", "free", "BitsDuJour (free)"),

    # ── Yandex / Russian promo blogs ──────────────────────────────────────
    ("yandex_blog", "https://yandex.ru/blog/yandex/rss", "yandex", "промо", "Yandex blog (промо)"),
    ("yandex_market_blog", "https://market.yandex.ru/journal/rss", "yandex", "промокод", "Yandex Market journal"),
    ("ozon_blog", "https://www.ozon.ru/highlight/blog/rss/", "ru-deals", "промокод", "Ozon blog"),
    ("wildberries_news", "https://wildberries.ru/news/rss", "ru-deals", "акция", "Wildberries news"),

    # ── Misc lifestyle freebies ──────────────────────────────────────────
    ("freebiehollow", "https://www.freebiehollow.com/feed/", "freebies", None, "FreebieHollow"),
    ("freebieshark", "https://www.freebieshark.com/feed/", "freebies", None, "FreebieShark"),
    ("ifreebies", "https://www.ifreebies.com/feed/", "freebies", None, "IFreebies"),
    ("hunt4freebies", "https://hunt4freebies.com/feed/", "freebies", None, "Hunt4Freebies"),
    ("freebiequeen13", "https://freebiequeen13.com/feed/", "freebies", None, "FreebieQueen13"),
    ("freebies4mom", "https://freebies4mom.com/feed/", "freebies", None, "Freebies4Mom"),
    ("freestufffinder", "https://www.freestufffinder.com/feed/", "freebies", None, "FreeStuffFinder"),
    ("freestufffinder_canada", "https://www.freestufffinder.ca/feed/", "freebies", None, "FreeStuffFinder Canada"),
    ("yofreesamples", "https://www.yofreesamples.com/feed/", "freebies", None, "YoFreeSamples"),
    ("guide2free", "https://www.guide2free.com/feed/", "freebies", None, "Guide2Free"),
    ("totallyfreestuff", "https://www.totallyfreestuff.com/rss.aspx", "freebies", None, "TotallyFreeStuff"),
    ("freeflys", "https://www.freeflys.com/freebies.rss", "freebies", None, "FreeFlys"),
    ("ifreesamples", "https://www.ifreesamples.com/feed/", "freebies", None, "IFreeSamples"),
    ("missfreebie", "https://www.missfreebie.com/feed/", "freebies", None, "MissFreebie"),
]

