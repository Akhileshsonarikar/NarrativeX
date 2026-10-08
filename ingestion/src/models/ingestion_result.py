from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SourceIngestionResult:
    source_id: str
    source_name: str
    fetched_count: int
    inserted_count: int
    duplicates_skipped: int
    status: str
    error_message: Optional[str] = None