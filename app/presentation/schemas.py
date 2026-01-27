from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.domain.offer import OfferType, OfferStatus, Offer

class OfferCreate(BaseModel):
    institution_id: UUID
    title: str
    description: Optional[str]
    type: OfferType
    publication_date: datetime
    application_deadline: datetime

class OfferUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    type: Optional[OfferType]
    status: Optional[OfferStatus]
    publication_date: Optional[datetime]
    application_deadline: Optional[datetime]

class OfferRead(BaseModel):
    id: UUID
    institution_id: UUID
    title: str
    description: Optional[str]
    type: OfferType
    status: OfferStatus
    publication_date: datetime
    application_deadline: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, offer: Offer):
        return cls(**offer.__dict__)
