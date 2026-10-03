from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Article(BaseModel):
    article_id: str
    source_id: str
    source_name: str

    title: str
    description: Optional[str] = None
    content: Optional[str] = None

    url: HttpUrl

    author: Optional[str] = None
    published_at: Optional[datetime] = None

    language: str = "en"
    category: Optional[str] = None

    ingested_at: datetime