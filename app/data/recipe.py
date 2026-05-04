from __future__ import annotations
from typing import Optional
from sqlmodel import Field

from .auditable_model import AuditableModel


class Recipe(AuditableModel, table=True):
    name: str
    description: Optional[str] = None
    servings: Optional[int] = None
    family_id: int = Field(foreign_key="family.id")
