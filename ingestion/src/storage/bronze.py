from dataclasses import dataclass
import json
from pathlib import Path
from typing import List

from ingestion.src.models.article import Article


@dataclass(frozen=True)
class BronzeWriteResult:
    output_file: Path
    inserted_count: int
    duplicates_skipped: int


class BronzeStorage:

    def __init__(self, base_path: str = "ingestion/data/bronze"):
        self.base_path = Path(base_path)

    def write_articles(self, articles: List[Article]) -> Path:

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = self.base_path / "articles.json"

        existing_articles = []

        if output_file.exists():
            with output_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                existing_articles = json.load(file)

        
        existing_ids = {
            article["article_id"]
            for article in existing_articles
        }

        new_articles = []

        for article in articles:
            if article.article_id in existing_ids:
                continue

            new_articles.append(
                article.model_dump(mode="json")
            )

            existing_ids.add(article.article_id)

        if new_articles:
            existing_articles.extend(new_articles)

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                existing_articles,
                file,
                indent=2,
                ensure_ascii=False,
            )
            
        return BronzeWriteResult(
    output_file=output_file,
    inserted_count=len(new_articles),
    duplicates_skipped=len(articles) - len(new_articles),
)