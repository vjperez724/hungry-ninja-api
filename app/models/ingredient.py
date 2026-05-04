from pydantic import BaseModel
from typing import Optional


class IngredientDTO(BaseModel):
    id: Optional[int] = None
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
