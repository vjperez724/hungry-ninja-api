from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class RecipeIngredient(AuditableModel, table=True):
    amount: float
    unit: str
    recipe_id: int = Field(foreign_key="recipe.id")
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id")
    linked_recipe_id: int | None = Field(default=None, foreign_key="recipe.id")
