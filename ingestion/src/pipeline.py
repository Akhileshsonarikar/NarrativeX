from ingestion.src.sources.rss import RSSNewsSource
from ingestion.src.storage.bronze import BronzeStorage


RSS_FEED_URL = "https://indianexpress.com/section/india/feed/"


def main():

    print("Starting NarrativeX news ingestion...")

    source = RSSNewsSource(
        source_id="indian-express",
        source_name="The Indian Express",
        feed_url=RSS_FEED_URL,
    )

    print(f"Fetching articles from {source.source_name}...")

    articles = source.fetch_articles()

    print(f"Articles fetched: {len(articles)}")

    storage = BronzeStorage()

    output_file = storage.write_articles(articles)

    print(f"Articles written to: {output_file}")


if __name__ == "__main__":
    main()