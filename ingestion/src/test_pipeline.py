from unittest.mock import MagicMock, patch

import pytest

from ingestion.src import pipeline


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
    fake_source.source_name = "Test Source"
    fake_source.fetch_articles.return_value = fake_articles

    fake_storage = MagicMock()

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

        pipeline.main()

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
