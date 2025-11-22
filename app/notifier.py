from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from telegram import Bot

from config.settings import get_settings
from .news_fetcher import NewsItem
from .sentiment import SummaryResult

logger = logging.getLogger(__name__)


def format_message(summary: SummaryResult, items: Iterable[NewsItem]) -> str:
    lines: list[str] = []
    lines.append("*Finance News Digest*")

    if summary.highlights:
        highlight_block = "\n\n".join(f"- {h}" for h in summary.highlights)
        lines.extend(["", highlight_block])

    market = summary.market_sentiment
    if market:
        lines.append("")
        lines.append("*Market Sentiment*")
        sentiment_lines: list[str] = []
        for key in ("btc", "eth", "broad_market"):
            data = market.get(key) or {}
            stance = (data.get("stance") or "neutral").title()
            confidence = data.get("confidence")
            if confidence is not None:
                sentiment_lines.append(f"- {key.upper()}: {stance} ({confidence}%)")
            else:
                sentiment_lines.append(f"- {key.upper()}: {stance}")
        lines.append("\n".join(sentiment_lines))

    source_block = "\n\n".join(f"- [{item.source}]({item.url}) - {item.title}" for item in items)
    lines.extend(["", "*Sources*", source_block])

    return "\n".join(lines)


class TelegramNotifier:
    def __init__(self, bot: Bot | None = None) -> None:
        settings = get_settings()
        self.bot = bot or Bot(token=settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id

    async def send(self, text: str) -> None:
        logger.info("Sending Telegram digest (%d chars)", len(text))
        # Send as plain text to avoid Markdown parsing errors from unescaped characters in titles.
        await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=None)

    def send_blocking(self, text: str) -> None:
        asyncio.run(self.send(text))
