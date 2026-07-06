from typing import Optional

from pydantic import BaseModel


class SuggestionDTO(BaseModel):
    id: Optional[int] = None
    suggestion: str
    reason: str
