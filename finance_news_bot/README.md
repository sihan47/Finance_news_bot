# Finance News Bot

Automates a 30-minute cycle that collects the latest finance headlines, summarizes sentiment with GPT, and pushes a concise brief to Telegram. Designed for a lightweight VPS deployment.

## Key Features
- **News ingestion**: fetch configurable feeds or APIs via pluggable fetchers.
- **AI summarization**: condense multiple stories and tag sentiment using OpenAI GPT‑5 mini.
- **Telegram delivery**: send formatted updates to a personal chat or channel.
- **Scheduler**: APScheduler job runs every 30 minutes; can also trigger manually.

## Project Layout
```
finance_news_bot/
├── app/
│   ├── __init__.py
│   ├── news_fetcher.py      # Source adapters
│   ├── sentiment.py         # GPT summarization helpers
│   ├── notifier.py          # Telegram client
│   └── scheduler.py         # Job orchestration
├── config/
│   └── settings.py          # Typed settings model and loaders
├── scripts/
│   └── run_once.py          # Manual trigger for a single cycle
├── tests/
│   └── test_news_fetcher.py # Smoke test template
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start
1. **Clone & install**
   ```bash
   git clone <repo-url> && cd finance_news_bot
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # fill in OpenAI & Telegram credentials plus any news API keys
   ```

3. **Run locally**
   ```bash
   python scripts/run_once.py           # run a single fetch/summarize/send cycle
   python -m app.scheduler              # start APScheduler loop (every 30 minutes)
   ```

## Deployment Notes
- Target a small VPS (>=1 vCPU, 1GB RAM). Install system packages: `python3.11`, `python3.11-venv`, `git`.
- Use systemd or cron to keep the scheduler running, e.g.:
  ```ini
  # /etc/systemd/system/finance-news-bot.service
  [Unit]
  Description=Finance News Bot
  After=network.target

  [Service]
  WorkingDirectory=/opt/finance_news_bot
  ExecStart=/opt/finance_news_bot/.venv/bin/python -m app.scheduler
  Restart=on-failure
  EnvironmentFile=/opt/finance_news_bot/.env

  [Install]
  WantedBy=multi-user.target
  ```
- Logs are emitted to stdout; direct them to journald, logrotate, or an external service as needed.

## Environment Variables
See `.env.example` for the full list. Essential keys:

| Variable | Description |
| -------- | ----------- |
| `OPENAI_API_KEY` | Required for GPT summarization |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Chat/channel ID that should receive updates |
| `NEWS_API_KEY` | Optional, depending on chosen news provider |

## Next Steps
- Implement concrete fetchers (e.g., NewsAPI, RSS) inside `app/news_fetcher.py`.
- Fine-tune GPT prompt templates in `app/sentiment.py`.
- Add persistence (SQLite or Redis) to avoid duplicate alerts.
- Extend tests in `tests/` to cover fetcher adapters and formatter output.
