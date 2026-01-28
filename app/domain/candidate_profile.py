from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class CandidateProfile:
    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        full_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        cpf: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[UUID] = None,
        deletion_reason: Optional[str] = None,
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.cpf = cpf
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
