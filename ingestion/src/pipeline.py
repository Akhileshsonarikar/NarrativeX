from pathlib import Path

from ingestion.src.config.loader import ConfigLoader
from ingestion.src.sources.rss import RSSNewsSource
from ingestion.src.storage.bronze import BronzeStorage


def main():

    print("Starting NarrativeX news ingestion...")

    config_path = Path("config/sources.yaml")

    config_loader = ConfigLoader(
        str(config_path)
    )

    config = config_loader.load()

    storage = BronzeStorage()

    for source_config in config["sources"]:

        if not source_config.get("enabled", True):
            continue

        source_type = source_config["type"]

        if source_type != "rss":
            raise ValueError(
                f"Unsupported source type: {source_type}"
            )

        source = RSSNewsSource(
            source_id=source_config["source_id"],
            source_name=source_config["source_name"],
            feed_url=source_config["feed_url"],
        )

        print(
            f"Fetching articles from "
            f"{source.source_name}..."
        )

        articles = source.fetch_articles()

        print(
            f"Articles fetched: {len(articles)}"
        )

        # Indentation fixed from here down
        write_result = storage.write_articles(
            articles
        )

        print(
            f"New articles written: "
            f"{write_result.inserted_count}"
        )

        print(
            f"Duplicates skipped: "
            f"{write_result.duplicates_skipped}"
        )

        print(
            f"Articles written to: "
            f"{write_result.output_file}"
        )


if __name__ == "__main__":
    main()