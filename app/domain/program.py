from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Program:
    def __init__(
        self,
        id: Optional[UUID] = None,
        institution_id: UUID = None,
        name: str = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[UUID] = None,
        deletion_reason: Optional[str] = None,
    ):
        self.id = id or uuid4()
        self.institution_id = institution_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
