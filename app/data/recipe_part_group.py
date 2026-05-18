from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .auditable_model import AuditableModel

if TYPE_CHECKING:
    from .instruction import Instruction
    from .recipe import Recipe
    from .recipe_ingredient import RecipeIngredient


class RecipePartGroup(AuditableModel, table=True):
    __tablename__ = "recipe_part_group"  # type: ignore
    name: str
    recipe_id: int = Field(foreign_key="recipe.id")
    recipe: "Recipe" = Relationship(back_populates="recipe_part_groups")
    instructions: list["Instruction"] = Relationship(
        back_populates="recipe_part_group", sa_relationship_kwargs={"lazy": "joined"}
    )
    recipe_ingredients: list["RecipeIngredient"] = Relationship(
        back_populates="recipe_part_group", sa_relationship_kwargs={"lazy": "joined"}
    )
