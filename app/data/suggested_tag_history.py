from sqlmodel import Field

from app.data.auditable_model import AuditableModel


class SuggestedTagHistory(AuditableModel, table=True):
    __tablename__ = "suggested_tag_history"  # type: ignore

    tag: str = Field(nullable=False)
    times_accepted: int = Field(default=0)
    times_rejected: int = Field(default=0)
    times_suggested: int = Field(default=1)
    family_member_id: int = Field(foreign_key="family_member.id")
