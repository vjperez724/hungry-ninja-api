from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING, List

from .auditable_model import AuditableModel

if TYPE_CHECKING:
    from .family_member import FamilyMember

class Family(AuditableModel, table=True):
    name: str = Field(index=True, unique=True)

    members: List["FamilyMember"] = Relationship(back_populates="family")
