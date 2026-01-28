from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Role:
    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str | None = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
