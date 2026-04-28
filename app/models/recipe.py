from pydantic import BaseModel
from typing import Optional

from app.models import Ingredient 


class Recipe(BaseModel):
    name: str    
    # Recipe ingredients are grouped by category, e.g. "dough", "filling", "topping"
    ingredients: dict[str, list[Ingredient]]    
    # Instructions are also grouped by category, e.g. "dough", "filling", "topping"
    instructions: Optional[dict[str, list[str]]] = None