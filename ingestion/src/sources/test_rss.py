from unittest.mock import MagicMock, patch

import pytest

from ingestion.src.sources.rss import RSSNewsSource


def test_rss_source_fetches_articles():

    fake_feed = MagicMock()

    fake_feed.bozo = False

    fake_feed.entries = [
        {
            "title": "Test News Article",
            "link": "https://example.com/test-article",
            "summary": "This is a test news article.",
        }
    ]

    with patch(
        "ingestion.src.sources.rss.feedparser.parse",
        return_value=fake_feed,
    ):

        source = RSSNewsSource(
            source_id="test-source",
            source_name="Test Source",
            feed_url="https://example.com/rss",
        )

        articles = source.fetch_articles()

    assert len(articles) == 1
    assert articles[0].title == "Test News Article"
    assert str(articles[0].url) == "https://example.com/test-article"


def test_rss_source_raises_error_for_invalid_feed():

    fake_feed = MagicMock()

    fake_feed.bozo = True
    fake_feed.entries = []

    with patch(
        "ingestion.src.sources.rss.feedparser.parse",
        return_value=fake_feed,
    ):

        source = RSSNewsSource(
            source_id="test-source",
            source_name="Test Source",
            feed_url="https://example.com/rss",
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to parse RSS feed",
        ):
            source.fetch_articles()