from datetime import datetime, timezone

import pytest

from pydantic import ValidationError

from ingestion.src.models.article import Article


def test_valid_article():
    article = Article(
        article_id="test-001",
        source_id="test-source",
        source_name="Test Source",
        title="NarrativeX test article",
        description="This is a test article.",
        url="https://example.com/article",
        published_at=datetime.now(timezone.utc),
        ingested_at=datetime.now(timezone.utc),
    )

    assert article.title == "NarrativeX test article"
    assert article.source_name == "Test Source"


def test_article_requires_title():
    with pytest.raises(ValidationError):
        Article(
            article_id="test-002",
            source_id="test-source",
            source_name="Test Source",
            url="https://example.com/article",
            ingested_at=datetime.now(timezone.utc),
        )


def test_article_requires_valid_url():
    with pytest.raises(ValidationError):
        Article(
            article_id="test-003",
            source_id="test-source",
            source_name="Test Source",
            title="Invalid URL test",
            url="not-a-valid-url",
            ingested_at=datetime.now(timezone.utc),
        )