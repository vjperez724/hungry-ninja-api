from pydantic import BaseModel
from typing import Optional


class Ingredient(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
