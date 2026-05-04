from sqlmodel import Field
from typing import Optional

from .auditable_model import AuditableModel


class RecipeIngredient(AuditableModel, table=True):
    __tablename__ = "recipe_ingredient"
    order: int
    amount: Optional[float] = None
    unit: Optional[str] = None
    group_id: int = Field(foreign_key="recipe_part_group.id")
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id")
    # This allows for a recipe ingredient to be linked to another recipe, which can be used for sub-recipes or components of a larger recipe.
    linked_recipe_id: int | None = Field(default=None, foreign_key="recipe.id")
