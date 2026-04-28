from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship

from .auditable_model import AuditableModel

if TYPE_CHECKING:
    from .family import Family

class FamilyMember(AuditableModel, table=True):
    name: str
    auth_id: str = Field(index=True, unique=True)
    family_id: int = Field(foreign_key="family.id")

    family: "Family" = Relationship(back_populates="members")
