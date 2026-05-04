from sqlmodel import Field

from .auditable_model import AuditableModel


class RecipePartGroup(AuditableModel, table=True):
    __tablename__ = "recipe_part_group"
    name: str
    recipe_id: int = Field(foreign_key="recipe.id")
