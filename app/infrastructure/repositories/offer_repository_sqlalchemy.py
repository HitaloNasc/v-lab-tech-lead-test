from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.orm import selectinload
from app.domain.offer import Offer, OfferType, OfferStatus
from app.domain.offer_repository import OfferRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import OfferModel
from datetime import datetime

class OfferRepositorySQLAlchemy(OfferRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, offer: Offer) -> Offer:
        async with self.session_factory() as session:
            db_offer = OfferModel.from_domain(offer)
            session.add(db_offer)
            await session.commit()
            await session.refresh(db_offer)
            return db_offer.to_domain()

    async def list(self, institution_id=None, type=None, status=None, limit=20, offset=0) -> List[Offer]:
        async with self.session_factory() as session:
            query = select(OfferModel).where(OfferModel.deleted_at.is_(None))
            if institution_id:
                query = query.where(OfferModel.institution_id == institution_id)
            if type:
                query = query.where(OfferModel.type == type)
            if status:
                query = query.where(OfferModel.status == status)
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return [row.to_domain() for row in result.scalars().all()]

    async def get_by_id(self, offer_id: UUID) -> Optional[Offer]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OfferModel).where(OfferModel.id == offer_id, OfferModel.deleted_at.is_(None))
            )
            db_offer = result.scalar_one_or_none()
            return db_offer.to_domain() if db_offer else None

    async def update(self, offer: Offer) -> Offer:
        async with self.session_factory() as session:
            db_offer = await session.get(OfferModel, offer.id)
            if not db_offer or db_offer.deleted_at:
                return None
            db_offer.update_from_domain(offer)
            db_offer.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_offer)
            return db_offer.to_domain()

    async def soft_delete(self, offer_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        async with self.session_factory() as session:
            db_offer = await session.get(OfferModel, offer_id)
            if db_offer and not db_offer.deleted_at:
                db_offer.deleted_at = datetime.utcnow()
                db_offer.deleted_by = deleted_by
                db_offer.deletion_reason = reason
                db_offer.status = OfferStatus.DELETED
                await session.commit()
