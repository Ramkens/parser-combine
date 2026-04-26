# parser-combine

Лёгкий универсальный комбайн-парсер на Python (asyncio + aiohttp), оптимизирован под бесплатный тариф Render (~512 МБ RAM, низкий CPU). Управляется через Telegram-бота и/или CLI. Результаты — `*.txt` по источникам в одном ZIP + единый Excel-файл с листами.

## Источники

- **Telegram** (web, `t.me/s/<channel>`) — без API, по ключевым словам. Список каналов задаётся через `extras.channels` или используется список по умолчанию.
- **2GIS** — публичный catalog API (org name, address, phone, site, category).
- **Lolz.live** — поиск по форуму (web).
- **Steam** — бесплатные/со скидкой игры.
- **Wildberries** — самые дешёвые товары + фильтр по скидке (search.wb.ru).
- **HeadHunter** — вакансии (api.hh.ru).
- **Habr** — статьи через RSS.
- **Reddit** — публичный `.json`.
- **Hacker News** — через Algolia API.
- **GitHub Trending** — daily/weekly/monthly.
- **Pikabu** — поиск.
- **Avito** — поиск (web; возможны временные блокировки).
- **VK** — публичные группы (web, m.vk.com).

## Архитектура

- `app/core/http.py` — общий aiohttp клиент с retries и rate-limit
- `app/core/ratelimit.py` — token bucket + semaphore (`HTTP_CONCURRENCY`, `HTTP_RPS`)
- `app/core/writer.py` — потоковая запись в `*.txt` и `*.jsonl` (без накопления в RAM)
- `app/parsers/` — независимые async-генераторы по источникам
- `app/output/packer.py` — ZIP + многолистный XLSX через openpyxl write-only
- `app/orchestrator.py` — параллельный запуск парсеров с ограничением concurrency
- `app/bot/bot.py` — Telegram-бот (aiogram v3) с админ-проверкой
- `app/server.py` — мини-HTTP сервер (`/healthz`, `/ping`) для Render free + cron-job.org keepalive
- `app/main.py` — поднимает сервер + бот

## Запуск локально

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=...   # для бота
export ADMIN_TG_ID=123456789
python -m app.main              # бот + сервер
# или CLI
python -m app.cli --sources wildberries,habr,reddit --keywords "скидка,новости" --limit 100
```

## Деплой на Render

Репозиторий содержит `render.yaml` (Blueprint). Шаги:

1. В Render создать Web Service → Blueprint → выбрать репо.
2. В Environment задать `TELEGRAM_BOT_TOKEN` и `ADMIN_TG_ID`.
3. Подождать первый билд. Health check ходит на `/healthz`.
4. На cron-job.org поставить пинг `https://<service>.onrender.com/ping` каждые 5 минут (для удержания инстанса от сна на free tier).

`Procfile` и `runtime.txt` тоже на месте — старые типы развёртывания тоже работают.

## Пример использования из Telegram

```
/start
/sources       — открыть инлайн-меню, нажать на нужные источники
/keywords ноутбук, скидка, акция
/limit 80
/run           — бот пришлёт прогресс, потом zip и xlsx
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | токен бота | (обязательно) |
| `ADMIN_TG_ID` | TG ID единственного админа | (обязательно) |
| `PORT` | порт HTTP сервера | `10000` |
| `HTTP_CONCURRENCY` | параллельных запросов всего | `6` |
| `HTTP_RPS` | глобальный лимит запросов в секунду | `4` |
| `HTTP_TIMEOUT` | таймаут на запрос (сек) | `25` |
| `HTTP_RETRIES` | ретраев на запрос | `3` |
| `OUTPUT_DIR` | папка с прогонами | `runs` |
| `LOG_LEVEL` | уровень логов | `INFO` |
| `USER_AGENT` | UA для HTTP | реалистичный Chrome |

## Память и стабильность

- Глобальные семафор + token bucket — нет всплесков нагрузки.
- Парсеры — async-генераторы; ничего не хранится в памяти кроме одной строки за раз.
- Запись в файл сразу после получения каждого row.
- XLSX строится в `write_only` режиме openpyxl — поток без полной матрицы в RAM.
- Авторестарт через Render + keepalive пинги cron-job.org.
