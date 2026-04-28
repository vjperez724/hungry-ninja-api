from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class Instruction(AuditableModel, table=True):
    step_number: int
    description: str
    recipe_id: int = Field(foreign_key="recipe.id")
