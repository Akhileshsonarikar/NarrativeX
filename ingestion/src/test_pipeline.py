from unittest.mock import MagicMock, patch
from pathlib import Path
from ingestion.src.storage.bronze import BronzeWriteResult
import pytest

from ingestion.src import pipeline
from ingestion.src.storage.bronze import BronzeWriteResult

def test_pipeline_continues_when_one_source_fails():

    fake_loader = MagicMock()

    fake_loader.load.return_value = {
        "sources": [
            {
                "source_id": "failing-source",
                "source_name": "Failing Source",
                "type": "rss",
                "feed_url": "https://example.com/failing",
                "enabled": True,
            },
            {
                "source_id": "working-source",
                "source_name": "Working Source",
                "type": "rss",
                "feed_url": "https://example.com/working",
                "enabled": True,
            },
        ]
    }

    failing_source = MagicMock()
    failing_source.source_id = "failing-source"
    failing_source.source_name = "Failing Source"
    failing_source.fetch_articles.side_effect = RuntimeError(
        "Simulated RSS failure"
    )

    working_source = MagicMock()
    working_source.source_id = "working-source"
    working_source.source_name = "Working Source"
    working_source.fetch_articles.return_value = [
        MagicMock()
    ]

    fake_storage = MagicMock()

    fake_storage.write_articles.return_value = BronzeWriteResult(
        output_file=Path("test-output/articles.json"),
        inserted_count=1,
        duplicates_skipped=0,
    )

    with patch(
        "ingestion.src.pipeline.ConfigLoader",
        return_value=fake_loader,
    ), patch(
        "ingestion.src.pipeline.RSSNewsSource",
        side_effect=[
            failing_source,
            working_source,
        ],
    ), patch(
        "ingestion.src.pipeline.BronzeStorage",
        return_value=fake_storage,
    ):

        results = pipeline.main()

    assert len(results) == 2

    assert results[0].status == "FAILED"
    assert results[0].source_id == "failing-source"
    assert results[0].error_message == "Simulated RSS failure"

    assert results[1].status == "SUCCESS"
    assert results[1].source_id == "working-source"

    assert (
        working_source.fetch_articles.call_count == 1
    )

    assert (
        fake_storage.write_articles.call_count == 1
    )


def test_pipeline_processes_enabled_rss_source():

    fake_articles = [
        MagicMock(),
        MagicMock(),
    ]

    fake_loader = MagicMock()
    fake_loader.load.return_value = {
        "sources": [
            {
                "source_id": "test-source",
                "source_name": "Test Source",
                "type": "rss",
                "feed_url": "https://example.com/rss",
                "enabled": True,
            }
        ]
    }

    fake_source = MagicMock()
    fake_source.source_id = "test-source"
    fake_source.source_name = "Test Source"
    fake_source.fetch_articles.return_value = fake_articles

    # Added missing initialization for fake_storage
    fake_storage = MagicMock()

    # Fixed indentation here
    fake_storage.write_articles.return_value = BronzeWriteResult(
        output_file=Path("test-output/articles.json"),
        inserted_count=2,
        duplicates_skipped=0,
    )

    with patch(
        "ingestion.src.pipeline.ConfigLoader",
        return_value=fake_loader,
    ) as mock_config_loader, patch(
        "ingestion.src.pipeline.RSSNewsSource",
        return_value=fake_source,
    ) as mock_rss_source, patch(
        "ingestion.src.pipeline.BronzeStorage",
        return_value=fake_storage,
    ) as mock_bronze_storage:

        results = pipeline.main()

    # Fixed indentation here so it aligns with the function body
    assert len(results) == 1
    assert results[0].source_id == "test-source"
    assert results[0].fetched_count == 2
    assert results[0].inserted_count == 2
    assert results[0].duplicates_skipped == 0

    mock_config_loader.assert_called_once_with(
        "config/sources.yaml"
    )

    fake_loader.load.assert_called_once()

    mock_rss_source.assert_called_once_with(
        source_id="test-source",
        source_name="Test Source",
        feed_url="https://example.com/rss",
    )

    fake_source.fetch_articles.assert_called_once()

    mock_bronze_storage.assert_called_once()

    fake_storage.write_articles.assert_called_once_with(
        fake_articles
    )


def test_pipeline_skips_disabled_source():

    fake_loader = MagicMock()
    fake_loader.load.return_value = {
        "sources": [
            {
                "source_id": "disabled-source",
                "source_name": "Disabled Source",
                "type": "rss",
                "feed_url": "https://example.com/rss",
                "enabled": False,
            }
        ]
    }

    fake_storage = MagicMock()

    with patch(
        "ingestion.src.pipeline.ConfigLoader",
        return_value=fake_loader,
    ), patch(
        "ingestion.src.pipeline.RSSNewsSource",
    ) as mock_rss_source, patch(
        "ingestion.src.pipeline.BronzeStorage",
        return_value=fake_storage,
    ):

        pipeline.main()

    mock_rss_source.assert_not_called()

    fake_storage.write_articles.assert_not_called()


def test_pipeline_rejects_unsupported_source_type():

    fake_loader = MagicMock()
    fake_loader.load.return_value = {
        "sources": [
            {
                "source_id": "test-api",
                "source_name": "Test API",
                "type": "api",
                "feed_url": "https://example.com/api",
                "enabled": True,
            }
        ]
    }

    with patch(
        "ingestion.src.pipeline.ConfigLoader",
        return_value=fake_loader,
    ):

        with pytest.raises(
            ValueError,
            match="Unsupported source type: api",
        ):
            pipeline.main()