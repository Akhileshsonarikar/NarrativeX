import hashlib
from datetime import datetime, timezone
from typing import List

import feedparser

from ingestion.src.models.article import Article
from ingestion.src.sources.base import NewsSource


class RSSNewsSource(NewsSource):

    def __init__(self, source_id: str, source_name: str, feed_url: str):
        self.source_id = source_id
        self.source_name = source_name
        self.feed_url = feed_url

    def fetch_articles(self) -> List[Article]:

        feed = feedparser.parse(self.feed_url)

        articles = []

        for entry in feed.entries:

            title = entry.get("title", "").strip()
            url = entry.get("link")

            if not title or not url:
                continue

            article_id = hashlib.sha256(
                url.encode("utf-8")
            ).hexdigest()# WE are creating article ID over here much like UUID 

            published_at = None

            if entry.get("published_parsed"):
                published_at = datetime(
                    *entry.published_parsed[:6],
                    tzinfo=timezone.utc
                )

            article = Article(
                article_id=article_id,
                source_id=self.source_id,
                source_name=self.source_name,
                title=title,
                description=entry.get("summary"),
                url=url,
                published_at=published_at,
                ingested_at=datetime.now(timezone.utc),
            )

            articles.append(article)

        return articles