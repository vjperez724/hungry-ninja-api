from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import timezone


class AuditableModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Optional[str] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)    
    updated_by: Optional[str] = Field(default=None)
    marked_for_deletion: Optional[bool] = Field(default=False, nullable=False)