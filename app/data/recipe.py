from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class Recipe(AuditableModel, table=True):
    name: str
    description: str
    servings: int
    family_id: int = Field(foreign_key="family.id")
