from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from app.domain.role import Role


class User:
    def __init__(
        self,
        id: Optional[UUID] = None,
        email: str = None,
        hashed_password: str = None,
        roles: Optional[List[Role]] = None,
        institution_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[UUID] = None,
        deletion_reason: Optional[str] = None,
    ):
        self.id = id or uuid4()
        self.email = email
        self.hashed_password = hashed_password
        # many-to-many roles collection (list of Role domain objects)
        self.roles = roles or []
        # optional association to an Institution
        self.institution_id = institution_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
