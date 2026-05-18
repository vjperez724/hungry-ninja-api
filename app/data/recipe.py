from typing import Optional

from sqlmodel import Field, Relationship

from .auditable_model import AuditableModel


class Recipe(AuditableModel, table=True):
    name: str
    description: Optional[str] = None
    servings: Optional[int] = None
    family_id: int = Field(foreign_key="family.id")
    recipe_part_groups: list["RecipePartGroup"] = Relationship(
        back_populates="recipe",
        sa_relationship_kwargs={"lazy": "joined"},
    )
