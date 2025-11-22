"""Utility script to print the exact prompt sent to GPT (without calling the API)."""

import asyncio
import datetime as dt
import logging
import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.news_fetcher import NewsAPIFetcher, NewsItem, collect  # noqa: E402
from app.sentiment import NewsSummarizer, SUMMARY_PROMPT  # noqa: E402
from config.settings import get_settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("print_prompt")


async def _fetch_or_dummy(settings) -> list[NewsItem]:
    fetcher = NewsAPIFetcher(api_key=settings.news_api_key, sources=settings.sources, limit=5)
    logger.info("Fetching sample news items...")
    try:
        items = await collect([fetcher])
        if items:
            return items
        logger.warning("No news items retrieved; using dummy samples instead.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Fetch failed (%s); using dummy samples instead.", exc)

    now = dt.datetime.utcnow()
    return [
        NewsItem(
            title="Fed signals no rate cuts until inflation cools further",
            url="https://example.com/fed",
            published_at=now,
            source="ExampleWire",
            summary="Policy makers cautious despite cooling CPI data.",
        ),
        NewsItem(
            title="BTC breaks above $70k on ETF inflows",
            url="https://example.com/btc",
            published_at=now - dt.timedelta(minutes=10),
            source="CryptoDesk",
            summary="Analysts cite strong spot ETF demand from US institutions.",
        ),
        NewsItem(
            title="Tech mega-cap earnings beat forecasts",
            url="https://example.com/earnings",
            published_at=now - dt.timedelta(minutes=20),
            source="MarketBeat",
            summary="Cloud and AI segments drive revenue surprise.",
        ),
    ]


async def main() -> None:
    settings = get_settings()
    if not settings.news_api_key:
        logger.info("NEWS_API_KEY missing; will use dummy news items only.")
    items = await _fetch_or_dummy(settings)

    summarizer = NewsSummarizer()
    content = summarizer.build_content(items[:5])

    print("\n=== SYSTEM PROMPT ===\n")
    print(SUMMARY_PROMPT.strip())
    print("\n=== USER CONTENT ===\n")
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
