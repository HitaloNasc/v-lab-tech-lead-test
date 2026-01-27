from sqlalchemy import Column, String, DateTime, Enum as SqlEnum, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime
from app.domain.offer import OfferType, OfferStatus, Offer

Base = declarative_base()

class OfferModel(Base):
    __tablename__ = "offers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    institution_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SqlEnum(OfferType), nullable=False, index=True)
    status = Column(SqlEnum(OfferStatus), nullable=False, index=True)
    publication_date = Column(DateTime(timezone=True), nullable=False)
    application_deadline = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    def to_domain(self) -> Offer:
        return Offer(
            id=self.id,
            institution_id=self.institution_id,
            title=self.title,
            description=self.description,
            type=self.type,
            status=self.status,
            publication_date=self.publication_date,
            application_deadline=self.application_deadline,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, offer: Offer) -> "OfferModel":
        return cls(
            id=offer.id,
            institution_id=offer.institution_id,
            title=offer.title,
            description=offer.description,
            type=offer.type,
            status=offer.status,
            publication_date=offer.publication_date,
            application_deadline=offer.application_deadline,
            created_at=offer.created_at,
            updated_at=offer.updated_at,
            deleted_at=offer.deleted_at,
            deleted_by=offer.deleted_by,
            deletion_reason=offer.deletion_reason,
        )

    def update_from_domain(self, offer: Offer):
        self.title = offer.title
        self.description = offer.description
        self.type = offer.type
        self.status = offer.status
        self.publication_date = offer.publication_date
        self.application_deadline = offer.application_deadline
        self.updated_at = datetime.utcnow()
        # Não atualiza deleted_at, deleted_by, deletion_reason aqui
