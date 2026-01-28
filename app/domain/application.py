from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Application:
    def __init__(
        self,
        id: Optional[UUID] = None,
        candidate_profile_id: Optional[UUID] = None,
        offer_id: Optional[UUID] = None,
        status: str = "submitted",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[UUID] = None,
        deletion_reason: Optional[str] = None,
    ):
        self.id = id or uuid4()
        self.candidate_profile_id = candidate_profile_id
        self.offer_id = offer_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
