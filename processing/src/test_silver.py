
import json
from datetime import datetime, timezone

from ingestion.src.models.article import Article
from processing.src.silver import SilverProcessor


def test_silver_normalizes_valid_records_and_quarantines_invalid_ones(
    tmp_path,
):
    bronze_path = tmp_path / "bronze" / "articles.json"
    silver_path = tmp_path / "silver" / "articles.json"
    rejected_path = tmp_path / "silver" / "rejected_articles.json"

    valid_record = Article(
        article_id="article-001",
        source_id="indian-express",
        source_name="The Indian Express",
        title="Placeholder",
        description="Placeholder",
        url="https://example.com/article-001",
        ingested_at=datetime.now(timezone.utc),
    ).model_dump(mode="json")

    valid_record["title"] = "  NarrativeX   Silver\n Test  "
    valid_record["description"] = "   "

    invalid_record = valid_record.copy()
    invalid_record["article_id"] = "article-002"
    invalid_record["title"] = "   "

    bronze_path.parent.mkdir(parents=True)
    bronze_path.write_text(
        json.dumps([valid_record, invalid_record]),
        encoding="utf-8",
    )

    processor = SilverProcessor(
        bronze_path=str(bronze_path),
        silver_path=str(silver_path),
        rejected_path=str(rejected_path),
    )

    result = processor.process()

    silver_records = json.loads(
        silver_path.read_text(encoding="utf-8")
    )
    rejected_records = json.loads(
        rejected_path.read_text(encoding="utf-8")
    )

    assert result["input_count"] == 2
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 1

    assert silver_records[0]["title"] == "NarrativeX Silver Test"
    assert silver_records[0]["description"] is None

    assert rejected_records[0]["record"]["article_id"] == "article-002"
    assert "title" in rejected_records[0]["error"]
