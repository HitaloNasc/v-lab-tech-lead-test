from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class OfferType(str, Enum):
    COURSE = "course"
    SCHOLARSHIP = "scholarship"
    INTERNSHIP = "internship"


class OfferStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    EXPIRED = "expired"
    DELETED = "deleted"


class Offer:
    def __init__(
        self,
        id: Optional[UUID] = None,
        institution_id: UUID = None,
        program_id: Optional[UUID] = None,
        title: str = None,
        description: str = None,
        type: OfferType = None,
        status: OfferStatus = OfferStatus.DRAFT,
        publication_date: Optional[datetime] = None,
        application_deadline: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[UUID] = None,
        deletion_reason: Optional[str] = None,
    ):
        self.id = id or uuid4()
        self.institution_id = institution_id
        self.program_id = program_id
        self.title = title
        self.description = description
        self.type = type
        self.status = status
        self.publication_date = publication_date
        self.application_deadline = application_deadline
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
