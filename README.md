# parser-combine — бесконечный парсер бесплатного

Постоянно работающий harvester публичных каталогов «бесплатного»: игр, предметов, скинов, ключей и giveaway. Управляется через Telegram-бота. Снимок (`ZIP` + `XLSX`) можно скачивать в любой момент во время парсинга. Деплоится на бесплатный план Render.

## Источники

| ключ | что собирает | ID |
|------|--------------|----|
| `steam` | все free-to-play и 100%-скидочные приложения Steam | `app:<appid>` |
| `roblox` | бесплатные предметы каталога (одежда, акс., анимации) | `asset:<assetId>` |
| `epic` | текущие и предстоящие бесплатные раздачи Epic Games Store | `epic:<offerId>` |
| `gog` | бесплатные игры в каталоге GOG | `gog:<id>` |
| `itchio` | бесплатные игры на itch.io (browse) | `itch:<id>` |
| `freetogame` | агрегатор всех F2P-игр (FreeToGame.com API) | `f2g:<id>` |
| `gamerpower` | все идущие giveaway: ключи, скины, валюта, DLC | `gp:<id>` |
| `reddit` | r/FreeGameFindings, r/freebies, r/GameDeals (только free), r/FreeGamesOnSteam | `reddit:<id>` |

Дедуп по стабильному ID — повторные показы одного и того же товара не дублируются. Каждый источник тикает по своему интервалу (Steam — раз в 30 мин, Roblox — 10 мин, Reddit — 5 мин и т.д.). Парсинг идёт в бесконечном цикле.

## Архитектура

```
app/
  core/       http (retries+rate-limit), token bucket, config, logger
  parsers/    8 источников + base + registry
  store.py    append-only writers (txt + jsonl + seen) с дедупом по id
  harvester.py infinite loop: per-source задачи с pause/resume/stop
  output/packer.py  снимок ZIP + многолистный XLSX из текущих файлов
  bot/bot.py  aiogram v3, админ-only
  server.py   /, /healthz, /ping (Render keepalive + cron-job.org)
  main.py     bootstrap всех трёх компонент
```

Память: ничего не накапливается в RAM кроме множества увиденных ID (sets); файлы только append, snapshot читается потоком, XLSX — `write_only` openpyxl. На free-tier Render держит несколько десятков MB RSS.

## Команды бота (админ)

```
/start        — стартует harvester и показывает меню/статус
/status       — счётчики и статус по каждому источнику
/download     — собрать снимок (ZIP + XLSX) и прислать прямо сейчас
/pause        — пауза (тики не выполняются)
/resume       — продолжить
/stop         — полная остановка фоновых задач
/reset        — обнулить базу (очистить все *.txt/*.jsonl/*.seen)
```

Снимок можно запрашивать сколько угодно раз — данные не блокируются, harvester продолжает писать.

## Запуск локально

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=...
export ADMIN_TG_ID=123456789
python -m app.main
```

## Render

`render.yaml` (Blueprint) уже на месте. Health check: `/healthz`. Внешний keepalive — cron-job.org → `https://<service>.onrender.com/ping` каждые 5 минут (бесплатный тариф засыпает через 15 мин idle).

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | токен бота | — |
| `ADMIN_TG_ID` | TG ID единственного админа | — |
| `OUTPUT_DIR` | папка с данными и снимками | `runs` |
| `HTTP_CONCURRENCY` | глобальный семафор | `6` |
| `HTTP_RPS` | глобальный лимит RPS | `4` |
| `HTTP_TIMEOUT` | таймаут на запрос (сек) | `25` |
| `HTTP_RETRIES` | ретраев на запрос | `3` |
| `LOG_LEVEL` | уровень логов | `INFO` |
| `USER_AGENT` | UA для HTTP | реалистичный Chrome |
| `PORT` | порт HTTP сервера | `10000` |
