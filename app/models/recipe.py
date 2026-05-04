from pydantic import BaseModel
from typing import Optional

from app.models import IngredientDTO 


class RecipeDTO(BaseModel):
    id: Optional[int] = None
    name: str    
    # Recipe ingredients are grouped by category, e.g. "dough", "filling", "topping"
    ingredients: dict[str, list[IngredientDTO]]    
    # Instructions are also grouped by category, e.g. "dough", "filling", "topping"
    instructions: Optional[dict[str, list[str]]] = None