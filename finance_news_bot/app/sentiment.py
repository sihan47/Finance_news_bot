from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List

from openai import OpenAI

from config.settings import get_settings
from .news_fetcher import NewsItem

logger = logging.getLogger(__name__)


SUMMARY_PROMPT = """You are an assistant that condenses finance and markets news into a concise bulletin.

For each article provided, output bullet points summarizing the key development and its likely market impact.
Then output an overall sentiment classification for BTC, ETH, and broad market (one of: bullish, neutral, bearish) with optional confidence 0-100.

Return the result strictly in JSON with:
{
  "highlights": ["- bullet", ...],
  "market_sentiment": {
     "btc": {"stance": "bullish|neutral|bearish", "confidence": 0-100},
     "eth": {...},
     "broad_market": {...}
  }
}
"""


@dataclass(slots=True)
class SummaryResult:
    highlights: List[str]
    market_sentiment: dict


class NewsSummarizer:
    def __init__(self, client: OpenAI | None = None) -> None:
        settings = get_settings()
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.model = settings.summarize_model
        self.show_prompt = settings.summarizer_show_prompt

    def build_content(self, items: Iterable[NewsItem]) -> str:
        lines: List[str] = []
        for item in items:
            lines.append(f"- {item.title} | {item.source} ({item.published_at.isoformat()})\n  URL: {item.url}")
            if item.summary:
                lines.append(f"  Summary: {item.summary}")
        return "\n".join(lines)

    def summarize(self, items: Iterable[NewsItem]) -> SummaryResult:
        content = self.build_content(items)
        if self.show_prompt:
            logger.info("Summarizer prompt:\n%s\n%s", SUMMARY_PROMPT, content[:2000])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        if not raw:
            raise RuntimeError("Empty response from OpenAI summarizer")

        import json

        payload = json.loads(raw)

        highlights = payload.get("highlights") or []
        market_sentiment = payload.get("market_sentiment") or {}
        return SummaryResult(highlights=list(highlights), market_sentiment=dict(market_sentiment))
