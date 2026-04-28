from pydantic import BaseModel
from typing import Optional


class Suggestion(BaseModel):
    suggestion: str
    reason: Optional[str] = None
