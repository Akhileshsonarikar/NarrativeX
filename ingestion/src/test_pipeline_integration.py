import json
from unittest.mock import MagicMock, patch

from ingestion.src import pipeline
from ingestion.src.storage.bronze import BronzeStorage


def test_pipeline_is_idempotent(tmp_path):

    fake_feed = MagicMock()

    fake_feed.bozo = False

    fake_feed.entries = [
        {
            "title": "Integration Test Article",
            "link": "https://example.com/integration-test",
            "summary": "Integration test article.",
        }
    ]

    storage = BronzeStorage(
        base_path=str(tmp_path / "bronze")
    )

    with patch(
        "ingestion.src.sources.rss.feedparser.parse",
        return_value=fake_feed,
    ), patch(
        "ingestion.src.pipeline.BronzeStorage",
        return_value=storage,
    ):

        # First ingestion run
        pipeline.main()

        # Second ingestion run with the exact same source data
        pipeline.main()

    output_file = tmp_path / "bronze" / "articles.json"

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        articles = json.load(file)

    assert len(articles) == 1

    assert articles[0]["title"] == "Integration Test Article"

    assert (
        articles[0]["url"]
        == "https://example.com/integration-test"
    )
