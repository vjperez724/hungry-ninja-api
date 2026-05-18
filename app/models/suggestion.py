from pydantic import BaseModel


class SuggestionDTO(BaseModel):
    suggestion: str
    reason: str
