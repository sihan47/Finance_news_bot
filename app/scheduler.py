from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import get_settings
from .news_fetcher import NewsAPIFetcher, collect
from .notifier import TelegramNotifier, format_message
from .sentiment import NewsSummarizer

logger = logging.getLogger(__name__)


async def run_cycle() -> None:
    settings = get_settings()
    fetchers = []

    if settings.news_api_key:
        fetchers.append(NewsAPIFetcher(api_key=settings.news_api_key, sources=settings.sources, limit=12))

    if not fetchers:
        logger.error("No news fetchers configured; set NEWS_API_KEY or implement custom fetcher.")
        return

    logger.info("Fetching news items...")
    items = await collect(fetchers)
    if not items:
        logger.warning("No news items retrieved; sending empty-cycle notification.")
        notifier = TelegramNotifier()
        await notifier.send("本輪未取得任何新聞，可能是來源限流或暫無新文章。")
        return

    top_items = items[:8]
    summarizer = NewsSummarizer()
    summary = summarizer.summarize(top_items)

    notifier = TelegramNotifier()
    message = format_message(summary, top_items[:5])
    await notifier.send(message)


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def start_scheduler() -> AsyncIOScheduler:
    configure_logging()
    settings = get_settings()
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger.from_crontab(settings.schedule_cron)
    scheduler.add_job(run_cycle, trigger, name="finance-news-cycle")
    scheduler.start()
    logger.info("Scheduler started with cron '%s'", settings.schedule_cron)

    # Kick off one run immediately on startup.
    loop = asyncio.get_event_loop()
    loop.create_task(run_cycle())
    logger.info("Initial run_cycle scheduled immediately.")

    return scheduler


def main() -> None:
    scheduler = start_scheduler()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
