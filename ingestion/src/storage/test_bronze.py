import json
from datetime import datetime, timezone

from ingestion.src.models.article import Article
from ingestion.src.storage.bronze import BronzeStorage


def create_article(article_id: str, title: str) -> Article:
    return Article(
        article_id=article_id,
        source_id="test-source",
        source_name="Test Source",
        title=title,
        url=f"https://example.com/{article_id}",
        ingested_at=datetime.now(timezone.utc),
    )


def load_articles(storage_path):
    with storage_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_bronze_storage_writes_new_articles(tmp_path):

    storage = BronzeStorage(
        base_path=str(tmp_path / "bronze")
    )

    articles = [
        create_article(
            "article-001",
            "First Test Article",
        ),
        create_article(
            "article-002",
            "Second Test Article",
        ),
    ]

    result = storage.write_articles(articles)

    assert result.inserted_count == 2
    assert result.duplicates_skipped == 0

    stored_articles = load_articles(
        result.output_file
    )

    assert len(stored_articles) == 2
    assert stored_articles[0]["article_id"] == "article-001"
    assert stored_articles[1]["article_id"] == "article-002"


def test_bronze_storage_skips_existing_articles(tmp_path):

    storage = BronzeStorage(
        base_path=str(tmp_path / "bronze")
    )

    article = create_article(
        "article-001",
        "First Test Article",
    )

    first_result = storage.write_articles(
        [article]
    )

    second_result = storage.write_articles(
        [article]
    )

    assert first_result.inserted_count == 1
    assert first_result.duplicates_skipped == 0

    assert second_result.inserted_count == 0
    assert second_result.duplicates_skipped == 1

    stored_articles = load_articles(
        second_result.output_file
    )

    assert len(stored_articles) == 1
    assert stored_articles[0]["article_id"] == "article-001"


def test_bronze_storage_handles_duplicates_within_same_batch(tmp_path):

    storage = BronzeStorage(
        base_path=str(tmp_path / "bronze")
    )

    article_1 = create_article(
        "article-001",
        "First Test Article",
    )

    article_2 = create_article(
        "article-002",
        "Second Test Article",
    )

    articles = [
        article_1,
        article_2,
        article_1,
        article_2,
    ]

    result = storage.write_articles(articles)

    assert result.inserted_count == 2
    assert result.duplicates_skipped == 2

    stored_articles = load_articles(
        result.output_file
    )

    ids = [
        article["article_id"]
        for article in stored_articles
    ]

    assert len(stored_articles) == 2
    assert len(set(ids)) == 2