from typing import List

from pydantic import BaseModel


class Msg(BaseModel):
    message: str


class ImportSummary(BaseModel):
    message: str
    imported_count: int
    failed_imports: List[dict]
