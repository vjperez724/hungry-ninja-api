from sqlmodel import Field

from .auditable_model import AuditableModel


class Family(AuditableModel, table=True):
    name: str = Field(index=True, unique=True)
