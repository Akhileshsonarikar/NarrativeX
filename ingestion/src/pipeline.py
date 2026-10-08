from pathlib import Path

from ingestion.src.config.loader import ConfigLoader
from ingestion.src.models.ingestion_result import SourceIngestionResult
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

    results = []

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

        try:

            print(
                f"Fetching articles from "
                f"{source.source_name}..."
            )

            articles = source.fetch_articles()

            print(
                f"Articles fetched: {len(articles)}"
            )

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

            results.append(
                SourceIngestionResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    fetched_count=len(articles),
                    inserted_count=(
                        write_result.inserted_count
                    ),
                    duplicates_skipped=(
                        write_result.duplicates_skipped
                    ),
                    status="SUCCESS",
                )
            )

        except Exception as error:

            error_message = str(error)

            print(
                f"ERROR: Failed to ingest "
                f"{source.source_name}: "
                f"{error_message}"
            )

            results.append(
                SourceIngestionResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    fetched_count=0,
                    inserted_count=0,
                    duplicates_skipped=0,
                    status="FAILED",
                    error_message=error_message,
                )
            )

            continue

    print()
    print("=" * 80)
    print("NarrativeX Ingestion Summary")
    print("=" * 80)

    print(
        f"{'Source':<25}"
        f"{'Status':<12}"
        f"{'Fetched':>10}"
        f"{'New':>10}"
        f"{'Duplicates':>15}"
    )

    print("-" * 80)

    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0

    for result in results:

        print(
            f"{result.source_name:<25}"
            f"{result.status:<12}"
            f"{result.fetched_count:>10}"
            f"{result.inserted_count:>10}"
            f"{result.duplicates_skipped:>15}"
        )

        total_fetched += result.fetched_count
        total_inserted += result.inserted_count
        total_duplicates += result.duplicates_skipped

    print("-" * 80)

    print(
        f"{'TOTAL':<25}"
        f"{'':<12}"
        f"{total_fetched:>10}"
        f"{total_inserted:>10}"
        f"{total_duplicates:>15}"
    )

    print("=" * 80)

    return results


if __name__ == "__main__":
    main()