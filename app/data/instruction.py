from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class Instruction(AuditableModel, table=True):
    order: int
    description: str
    group_id: int = Field(foreign_key="recipe_part_group.id")
