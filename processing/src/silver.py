
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ingestion.src.models.article import Article


TEXT_FIELDS = (
    "article_id",
    "source_id",
    "source_name",
    "title",
    "description",
    "content",
    "author",
    "category",
    "language",
)

OPTIONAL_TEXT_FIELDS = {
    "description",
    "content",
    "author",
    "category",
}

REQUIRED_TEXT_FIELDS = (
    "article_id",
    "source_id",
    "source_name",
    "title",
    "url",
)


def normalize_and_validate(record: Any) -> Article:
    """Normalize one Bronze record and validate its Article contract."""

    if not isinstance(record, dict):
        raise ValueError("Article record must be a JSON object")

    normalized = record.copy()

    # Standardize whitespace and blank optional text fields.
    for field in TEXT_FIELDS:
        value = normalized.get(field)

        if isinstance(value, str):
            value = " ".join(value.split())

            if field in OPTIONAL_TEXT_FIELDS and not value:
                value = None

            normalized[field] = value

    # Remove accidental whitespace around URLs.
    if isinstance(normalized.get("url"), str):
        normalized["url"] = normalized["url"].strip()

    # A field can exist but still contain no meaningful value.
    for field in REQUIRED_TEXT_FIELDS:
        value = normalized.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Required field '{field}' must not be blank"
            )

    return Article.model_validate(normalized)


class SilverProcessor:
    def __init__(
        self,
        bronze_path: str = "ingestion/data/bronze/articles.json",
        silver_path: str = "processing/data/silver/articles.json",
        rejected_path: str = (
            "processing/data/silver/rejected_articles.json"
        ),
    ):
        self.bronze_path = Path(bronze_path)
        self.silver_path = Path(silver_path)
        self.rejected_path = Path(rejected_path)

    def process(self) -> dict:
        with self.bronze_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            bronze_records = json.load(file)

        if not isinstance(bronze_records, list):
            raise ValueError(
                "Bronze input must contain a JSON array of articles"
            )

        silver_records = []
        rejected_records = []

        for record_number, record in enumerate(
            bronze_records,
            start=1,
        ):
            try:
                article = normalize_and_validate(record)

                silver_records.append(
                    article.model_dump(mode="json")
                )

            except (ValidationError, ValueError, TypeError) as error:
                rejected_records.append(
                    {
                        "record_number": record_number,
                        "record": record,
                        "error": str(error),
                    }
                )

        self.silver_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.rejected_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.silver_path.write_text(
            json.dumps(
                silver_records,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.rejected_path.write_text(
            json.dumps(
                rejected_records,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return {
            "input_count": len(bronze_records),
            "accepted_count": len(silver_records),
            "rejected_count": len(rejected_records),
            "silver_path": str(self.silver_path),
            "rejected_path": str(self.rejected_path),
        }


def main():
    result = SilverProcessor().process()

    print("NarrativeX Silver Processing Summary")
    print(f"Bronze records read: {result['input_count']}")
    print(f"Silver records accepted: {result['accepted_count']}")
    print(f"Records rejected: {result['rejected_count']}")
    print(f"Silver output: {result['silver_path']}")
    print(f"Rejected records: {result['rejected_path']}")


if __name__ == "__main__":
    main()
