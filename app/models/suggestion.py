from pydantic import BaseModel
from typing import Optional


class SuggestionDTO(BaseModel):
    suggestion: str
    reason: Optional[str] = None
