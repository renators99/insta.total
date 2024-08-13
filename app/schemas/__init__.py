from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    result_count: int
    date_range: str
    results: List[str]

class SearchRequest(BaseModel):
    search_term: str
    date_option: int

