import asyncio
import datetime as dt

from app.news_fetcher import NewsItem, collect


class DummyFetcher:
    def __init__(self) -> None:
        self.called = False

    async def fetch(self):
        self.called = True
        return [
            NewsItem(
                title="Sample headline",
                url="https://example.com/news",
                published_at=dt.datetime.utcnow(),
                source="Example",
            )
        ]


def test_collect_runs_event_loop():
    fetcher = DummyFetcher()
    items = asyncio.run(collect([fetcher]))
    assert fetcher.called
    assert len(items) == 1
    assert items[0].title == "Sample headline"
