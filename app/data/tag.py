from __future__ import annotations
from sqlmodel import Field

from .auditable_model import AuditableModel


class Tag(AuditableModel, table=True):
    name: str = Field(index=True, unique=True)
    family_id: int = Field(foreign_key="family.id")
