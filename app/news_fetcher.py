from __future__ import annotations

import asyncio
import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List, Protocol

import httpx
from httpx import HTTPStatusError


@dataclass(slots=True)
class NewsItem:
    title: str
    url: str
    published_at: dt.datetime
    source: str
    summary: str | None = None


class NewsFetcher(Protocol):
    async def fetch(self) -> Iterable[NewsItem]:
        ...


class NewsAPIClient:
    """Minimal NewsAPI wrapper for top-headlines finance category."""

    def __init__(self, api_key: str, session: httpx.AsyncClient | None = None) -> None:
        self.api_key = api_key
        self._session = session or httpx.AsyncClient(timeout=10.0)
        self._owns_session = session is None

    async def __aenter__(self) -> "NewsAPIClient":
        return self

    async def __aexit__(self, *exc_info) -> None:  # type: ignore[override]
        if self._owns_session:
            await self._session.aclose()

    async def fetch_top_headlines(self, sources: list[str] | None = None, limit: int = 10) -> List[NewsItem]:
        params: dict[str, str] = {
            "category": "business",
            "language": "en",
            "pageSize": str(limit),
        }
        if sources:
            params["sources"] = ",".join(sources)

        response = await self._session.get(
            "https://newsapi.org/v2/top-headlines",
            params=params,
            headers={"X-Api-Key": self.api_key},
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            # Handle rate limiting gracefully to avoid crashing the whole cycle.
            if exc.response.status_code == 429:
                return []
            raise
        payload = response.json()

        results: List[NewsItem] = []
        for article in payload.get("articles", []):
            published_at = article.get("publishedAt")
            try:
                parsed_ts = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00")) if published_at else dt.datetime.utcnow()
            except Exception:
                parsed_ts = dt.datetime.utcnow()

            results.append(
                NewsItem(
                    title=article.get("title", "(no title)"),
                    url=article.get("url", ""),
                    published_at=parsed_ts,
                    source=article.get("source", {}).get("name", "Unknown"),
                    summary=article.get("description"),
                )
            )
        return results


class NewsAPIFetcher:
    def __init__(self, api_key: str, sources: list[str] | None = None, limit: int = 10) -> None:
        if not api_key:
            raise ValueError("NewsAPI key is required for NewsAPIFetcher")
        self.api_key = api_key
        self.sources = sources or []
        self.limit = limit

    async def fetch(self) -> Iterable[NewsItem]:
        async with NewsAPIClient(self.api_key) as client:
            return await client.fetch_top_headlines(self.sources, limit=self.limit)


async def collect(fetchers: list[NewsFetcher]) -> List[NewsItem]:
    """Run all fetchers concurrently and merge results."""

    async def _run(fetcher: NewsFetcher) -> List[NewsItem]:
        items = await fetcher.fetch()
        return list(items)

    results = await asyncio.gather(*[_run(f) for f in fetchers], return_exceptions=False)
    combined: List[NewsItem] = []
    for items in results:
        combined.extend(items)

    # sort by published time desc and remove duplicates by URL
    seen: set[str] = set()
    unique: List[NewsItem] = []
    for item in sorted(combined, key=lambda x: x.published_at, reverse=True):
        if not item.url or item.url in seen:
            continue
        seen.add(item.url)
        unique.append(item)
    return unique
