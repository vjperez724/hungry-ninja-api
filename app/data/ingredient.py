from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .auditable_model import AuditableModel

if TYPE_CHECKING:
    from .recipe_ingredient import RecipeIngredient


class Ingredient(AuditableModel, table=True):
    name: str = Field(index=True)
    family_id: int = Field(foreign_key="family.id")
    ingredients: list["RecipeIngredient"] = Relationship(back_populates="ingredient")
