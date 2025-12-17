# 🤖 tg-ytdlp-bot

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyroTGFork](https://img.shields.io/badge/PyroTGFork-Latest-green.svg)](https://github.com/pyrogram/pyrogram)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![gallery-dl](https://img.shields.io/badge/gallery--dl-Latest-orange.svg)](https://github.com/mikf/gallery-dl)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Advanced Telegram bot (PyroTGFork + yt-dlp + gallery-dl) for downloading video, audio, and images from YouTube, TikTok, Instagram, and hundreds of other sources. Supports rich format selection, cookie management, optional proxies, YouTube PO tokens, Firebase cache, and a FastAPI dashboard.

## ✨ Features

- Multi-site downloads (video/audio/images) via yt-dlp and gallery-dl with playlist support
- Multi-language responses: English, Arabic, Russian, Hindi (`/lang`)
- Format control: Always Ask menu, `/format` codec/MKV preferences, `/list` to show IDs, `/link` for direct stream URLs
- Cookie workflow: `/cookie`, `/check_cookie`, `/cookies_from_browser`, multi-source HTTP cookie URLs, fallback `TXT/cookie.txt`
- Proxy switching and PO token provider for YouTube; optional local-save mode per user
- NSFW blur toggle, tag system (`#tag`), rate/flood protection, allowed-group guard, optional channel subscription guard
- Dashboard (FastAPI + Jinja) on `DASHBOARD_PORT` for stats/config + bgutil PO token provider service in Docker
- Maintenance helpers: updater script, backup/restore scripts, Firebase cache auto-reload

## Project Layout

- `magic.py` — main bot entrypoint
- `CONFIG/` — `_config.py` template, per-language messages (EN/AR/RU/IN), domains/limits, secrets in `config.py` (gitignored)
- `COMMANDS/`, `DOWN_AND_UP/`, `URL_PARSERS/`, `HELPERS/` — bot handlers, download/upload helpers, URL parsing, utilities
- `web/` — FastAPI dashboard (`uvicorn web.dashboard_app:app`)
- `docker-compose.yml` + `docker/` — compose stack with bot, cookie webserver, bgutil PO provider
- `_etc/systemd/system/` — service templates for bare-metal
- Utility scripts: `run_bot.bat` (Windows), `UPDATE.sh`/`update_from_repo.py`, `create_backup.py`, `restore_from_backup.py`, `generate_session_string.py`

## Prerequisites

- Python 3.11 (recommended), git
- ffmpeg installed and on PATH (required for merges, audio extraction, subtitles)
- For dashboard: dependencies are in `requirements.txt`
- Optional: Docker/Compose, Firebase credentials, YouTube cookies

## Configuration (required before running)

1) Copy the template and edit:

```bash
cp CONFIG/_config.py CONFIG/config.py
```

2) Fill required fields in `CONFIG/config.py`:
- `BOT_NAMESPACE`, `BOT_NAME`, `BOT_NAME_FOR_USERS` (keep the same value), `ADMIN` list, `ALLOWED_GROUP` (IDs to serve in groups)
- `API_ID`, `API_HASH`, `BOT_TOKEN`
- Logging channels: `LOGS_ID`, `LOGS_VIDEO_ID`, `LOGS_IMG_ID`, `LOGS_NSFW_ID`, `LOGS_PAID_ID`, `LOG_EXCEPTION`
- Optional subscription gate: `SUBSCRIBE_CHANNEL`, `SUBSCRIBE_CHANNEL_URL`

3) Cookies:
- Default `YOUTUBE_COOKIE_URL` points to `http://127.0.0.1:8080/youtube.txt` (a simple HTTP server started by `run_bot.bat` from the local `cookies/` folder). Put Netscape-format cookies in `cookies/youtube.txt` (and other services if needed).
- Keep a fallback cookie in `TXT/cookie.txt` (`Config.COOKIE_FILE_PATH`) so yt-dlp/gallery-dl can read it directly.
- For Docker, place files under `docker/configuration-webserver/site/cookies/` and use URLs like `http://configuration-webserver/cookies/youtube.txt`. Up to 10 YouTube cookie URLs are supported (`YOUTUBE_COOKIE_URL_1..._10`).

4) Downloads and networking:
- `LOCAL_SAVE_ENABLED`, `LOCAL_SAVE_BASE_PATH`, `LOCAL_SAVE_SHARE_BASE` — save to disk instead of uploading to Telegram.
- `PROXY_*` and `PROXY_SELECT` — up to two proxies, switchable via `/proxy`.
- `YOUTUBE_POT_ENABLED`, `YOUTUBE_POT_BASE_URL` — PO token provider for YouTube (compose service `bgutil-provider:4416` by default).

5) Cache and telemetry:
- Firebase (optional): set `USE_FIREBASE`, `FIREBASE_CONF`, `BOT_DB_PATH`, `FIREBASE_CACHE_FILE`, `AUTO_CACHE_RELOAD_ENABLED`, `RELOAD_CACHE_EVERY` (hours). Cache dump is kept in `dump.json`.

6) Dashboard:
- `DASHBOARD_PORT`, `DASHBOARD_USERNAME`, `DASHBOARD_PASSWORD` control the FastAPI dashboard login and port.

7) Subscription guard / channel guard:
- If you gate access by channel, set `SUBSCRIBE_CHANNEL` and optionally `CHANNEL_GUARD_SESSION_STRING` (user session string to read channel admin logs).

## Getting Started

### Windows (recommended quick start)

1) Install Python 3.11 (tick “Add to PATH” and enable the `py` launcher).  
2) Configure `CONFIG/config.py` and cookie files as above.  
3) Run `run_bot.bat` from the project root. It will:
- Create/update `venv` (rebuild if Python version mismatches)
- Install `requirements.txt` (only once; tracked via `.deps_installed`)
- Start a local HTTP cookie server on **8080** serving the `cookies/` folder
- Register a Windows scheduled task `telegram-downloader-bot` to auto-start on logon
- Launch the bot (`magic.py`); logs are in `run_bot.log` and `bot.log`

Re-run `run_bot.bat` for manual starts; the scheduled task will keep it running after login.

### Manual install (Linux/macOS/Windows)

```bash
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
# ensure ffmpeg is installed (e.g. sudo apt install ffmpeg)
python magic.py
```

- If you keep cookie URLs pointing to `127.0.0.1:8080`, start a simple server: `python -m http.server 8080 -d cookies` (or change `YOUTUBE_COOKIE_URL` to your own endpoint).
- Start the dashboard when needed:

```bash
python -m uvicorn web.dashboard_app:app --host 0.0.0.0 --port <Config.DASHBOARD_PORT>
```

### Docker Compose

1) `cp .env.example .env` and set `COMPOSE_PROJECT_NAME`, `TZ`.  
2) Ensure `CONFIG/config.py` exists and cookie URLs point to `http://configuration-webserver/...`; `YOUTUBE_POT_BASE_URL` should be `http://bgutil-provider:4416`.  
3) Put cookie files under `docker/configuration-webserver/site/cookies/` before starting.  
4) Run:

```bash
docker compose up -d --build
```

The bot and dashboard start together; the dashboard is exposed on `5555` by default (map the port if you change `DASHBOARD_PORT`).

## Commands (high level)

User-facing:
- `/start`, `/help` — intro and help
- `/lang` — switch language (EN/AR/RU/IN)
- `/keyboard` — change reply keyboard layout (off/1x3/2x3/full)
- `/audio <url>`, `/playlist <url>`, send any URL to download video
- `/img <url>` — download images via gallery-dl
- `/format [ask|best|720|4k|id <n>]` — quality/codec/MKV preferences
- `/list <url>` — list available format IDs
- `/link [quality] <url>` — return direct stream links
- `/subs <lang|off>` — subtitle embed/delivery
- `/mediainfo on|off` — toggle mediainfo output
- `/split <size>` — split large files (MB/GB)
- `/args` — set custom yt-dlp arguments (grouped menu)
- `/proxy on|off|1|2` — switch between configured proxies
- `/cookie`, `/cookies_from_browser`, `/check_cookie`, `/save_as_cookie` — cookie management/validation
- `/tags` — list your tags (`#tag` in captions), `/search` — inline search helper
- `/nsfw on|off` — blur/allow NSFW previews
- `/usage` — your download history/logs
- `/clean` — clear caches/settings (args/nsfw/proxy/flood_wait)

Admin-only (IDs in `Config.ADMIN`):
- `/block_user`, `/unblock_user`, `/ban_time`
- `/usage` (full stats), `/log`, `/run_time`
- `/broadcast`, `/add_bot_to_group`
- Cache controls: `/auto_cache`, `/reload_cache`, `/uncache`

Group mode: add group IDs to `ALLOWED_GROUP` to enable handling in those groups.

## Dashboard

FastAPI app (`web/dashboard_app.py`) showing active users, top domains/downloaders, system metrics, and editable config fields (including cookie URLs and dashboard creds). Credentials and port come from `CONFIG/config.py`. Session data is stored in `CONFIG/.dashboard_sessions.json`. The dashboard is started automatically in Docker; for bare-metal run the uvicorn command above or use the systemd template in `_etc/systemd/system/tg-ytdlp-dashboard.service`.

## Maintenance

- **Updates:** `python update_from_repo.py` or `./UPDATE.sh` (uses git; preserves `CONFIG/config.py`, cookies, users, cache). Review the script before running in production.
- **Backups:** `python create_backup.py` to snapshot config/text/user data; `python restore_from_backup.py` to restore by backup ID.
- **Firebase cache:** `DATABASE/download_firebase.py` refreshes `dump.json`; enable `AUTO_CACHE_RELOAD_ENABLED` for periodic reload.
- **Services:** systemd templates live in `_etc/systemd/system/`; Docker entrypoint runs both bot and dashboard.

## Troubleshooting

- Check `run_bot.log`/`bot.log` for startup or download errors.
- Verify `ffmpeg` is installed and on PATH.
- Re-export cookies if YouTube starts failing; update `cookies/youtube.txt` and `TXT/cookie.txt`.
- Confirm `API_ID/API_HASH/BOT_TOKEN` and log channel IDs in `CONFIG/config.py`; add group IDs to `ALLOWED_GROUP` if the bot ignores groups.

## License

MIT — see `LICENSE`.
