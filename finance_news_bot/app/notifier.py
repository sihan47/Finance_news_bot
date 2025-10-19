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
    lines.append("")

    for highlight in summary.highlights:
        lines.append(f"- {highlight}")

    market = summary.market_sentiment
    if market:
        lines.append("")
        lines.append("*Market Sentiment*")
        for key in ("btc", "eth", "broad_market"):
            data = market.get(key) or {}
            stance = (data.get("stance") or "neutral").title()
            confidence = data.get("confidence")
            if confidence is not None:
                lines.append(f"- {key.upper()}: {stance} ({confidence}%)")
            else:
                lines.append(f"- {key.upper()}: {stance}")

    lines.append("")
    lines.append("*Sources*")
    for item in items:
        lines.append(f"- [{item.source}]({item.url}) - {item.title}")

    return "\n".join(lines)


class TelegramNotifier:
    def __init__(self, bot: Bot | None = None) -> None:
        settings = get_settings()
        self.bot = bot or Bot(token=settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id

    async def send(self, text: str) -> None:
        logger.info("Sending Telegram digest (%d chars)", len(text))
        await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")

    def send_blocking(self, text: str) -> None:
        asyncio.run(self.send(text))
