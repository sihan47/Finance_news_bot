import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_list(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    lowered = raw.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    news_api_key: str | None
    finnhub_api_key: str | None
    schedule_cron: str
    log_level: str
    sources: List[str]
    summarize_model: str = "gpt-5-mini"
    summarizer_show_prompt: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    openai_key = os.getenv("OPENAI_API_KEY", "")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is required")
    if not telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    if not telegram_chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is required")

    return Settings(
        openai_api_key=openai_key,
        telegram_bot_token=telegram_token,
        telegram_chat_id=telegram_chat_id,
        news_api_key=os.getenv("NEWS_API_KEY"),
        finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
        schedule_cron=os.getenv("SCHEDULE_CRON", "*/30 * * * *"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        sources=_parse_list(os.getenv("NEWS_SOURCES")),
        summarize_model=os.getenv("OPENAI_SUMMARIZE_MODEL", "gpt-5-mini"),
        summarizer_show_prompt=_env_bool("SUMMARIZER_SHOW_PROMPT", False),
    )
