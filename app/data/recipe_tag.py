from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class RecipeTag(AuditableModel, table=True):
    __tablename__ = "recipe_tag"
    recipe_id: int = Field(foreign_key="recipe.id")
    tag_id: int = Field(foreign_key="tag.id")
