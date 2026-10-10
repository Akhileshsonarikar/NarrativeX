import logging
from pathlib import Path

from ingestion.src.config.loader import ConfigLoader
from ingestion.src.logging_config import configure_logging
from ingestion.src.models.ingestion_result import SourceIngestionResult
from ingestion.src.sources.rss import RSSNewsSource
from ingestion.src.storage.bronze import BronzeStorage


logger = logging.getLogger(__name__)


def main():

    configure_logging()

    logger.info("Starting NarrativeX news ingestion")

    config_path = Path("config/sources.yaml")

    config_loader = ConfigLoader(str(config_path))
    config = config_loader.load()

    storage = BronzeStorage()
    results = []

    for source_config in config["sources"]:

        if not source_config.get("enabled", True):
            logger.info(
                "Skipping disabled source | source_id=%s",
                source_config.get("source_id", "unknown"),
            )
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

        fetched_count = 0

        try:
            logger.info(
                "Fetching source | source_id=%s source_name=%s",
                source.source_id,
                source.source_name,
            )

            articles = source.fetch_articles()
            fetched_count = len(articles)

            logger.info(
                "Articles fetched | source_id=%s fetched_count=%d",
                source.source_id,
                fetched_count,
            )

            write_result = storage.write_articles(articles)

            logger.info(
                "Bronze write completed | source_id=%s "
                "inserted_count=%d duplicates_skipped=%d "
                "output_file=%s",
                source.source_id,
                write_result.inserted_count,
                write_result.duplicates_skipped,
                write_result.output_file,
            )

            results.append(
                SourceIngestionResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    fetched_count=fetched_count,
                    inserted_count=write_result.inserted_count,
                    duplicates_skipped=write_result.duplicates_skipped,
                    status="SUCCESS",
                )
            )

        except Exception as error:
            error_message = str(error)

            logger.exception(
                "Source ingestion failed | source_id=%s "
                "source_name=%s",
                source.source_id,
                source.source_name,
            )

            results.append(
                SourceIngestionResult(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    fetched_count=fetched_count,
                    inserted_count=0,
                    duplicates_skipped=0,
                    status="FAILED",
                    error_message=error_message,
                )
            )

            continue

    total_fetched = sum(
        result.fetched_count for result in results
    )
    total_inserted = sum(
        result.inserted_count for result in results
    )
    total_duplicates = sum(
        result.duplicates_skipped for result in results
    )
    failed_sources = sum(
        result.status == "FAILED" for result in results
    )

    summary_lines = [
        "=" * 80,
        "NarrativeX Ingestion Summary",
        "=" * 80,
        (
            f"{'Source':<25}"
            f"{'Status':<12}"
            f"{'Fetched':>10}"
            f"{'New':>10}"
            f"{'Duplicates':>15}"
        ),
        "-" * 80,
    ]

    for result in results:
        summary_lines.append(
            f"{result.source_name:<25}"
            f"{result.status:<12}"
            f"{result.fetched_count:>10}"
            f"{result.inserted_count:>10}"
            f"{result.duplicates_skipped:>15}"
        )

    summary_lines.extend(
        [
            "-" * 80,
            (
                f"{'TOTAL':<25}"
                f"{'':<12}"
                f"{total_fetched:>10}"
                f"{total_inserted:>10}"
                f"{total_duplicates:>15}"
            ),
            f"Failed sources: {failed_sources}",
            "=" * 80,
        ]
    )

    logger.info("Ingestion summary:\n%s", "\n".join(summary_lines))

    return results


if __name__ == "__main__":
    main()