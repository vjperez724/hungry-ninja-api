from sqlmodel import Field

from .auditable_model import AuditableModel


class FamilyMember(AuditableModel, table=True):
    __tablename__ = "family_member"
    name: str
    auth_id: str = Field(index=True, unique=True)
    family_id: int = Field(foreign_key="family.id")
