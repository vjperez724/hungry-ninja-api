from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .auditable_model import AuditableModel

if TYPE_CHECKING:
    from .recipe_part_group import RecipePartGroup


class Instruction(AuditableModel, table=True):
    order: int
    description: str
    group_id: int = Field(foreign_key="recipe_part_group.id")
    recipe_part_group: "RecipePartGroup" = Relationship(back_populates="instructions")
