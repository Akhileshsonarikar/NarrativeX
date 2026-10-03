from abc import ABC, abstractmethod
from typing import List

from ingestion.src.models.article import Article


class NewsSource(ABC):

    @abstractmethod
    def fetch_articles(self) -> List[Article]:
        """
        Fetch articles from a news source.

        Every concrete source adapter must implement this method.
        """
        pass