import yaml
import pytest

from ingestion.src.config.loader import ConfigLoader


def test_config_loader_loads_valid_configuration(tmp_path):

    config_file = tmp_path / "sources.yaml"

    config_data = {
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

    with config_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        yaml.safe_dump(config_data, file)

    loader = ConfigLoader(str(config_file))

    config = loader.load()

    assert "sources" in config
    assert len(config["sources"]) == 1
    assert config["sources"][0]["source_id"] == "test-source"
    assert config["sources"][0]["enabled"] is True


def test_config_loader_raises_error_for_missing_file(tmp_path):

    config_file = tmp_path / "missing.yaml"

    loader = ConfigLoader(str(config_file))

    with pytest.raises(
        FileNotFoundError,
        match="Configuration file not found",
    ):
        loader.load()


def test_config_loader_raises_error_for_empty_file(tmp_path):

    config_file = tmp_path / "empty.yaml"

    config_file.write_text(
        "",
        encoding="utf-8",
    )

    loader = ConfigLoader(str(config_file))

    with pytest.raises(
        ValueError,
        match="Configuration file is empty",
    ):
        loader.load()
