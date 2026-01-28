from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.domain.application_repository import ApplicationRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import ApplicationModel
from datetime import datetime
from app.domain.errors import ConflictError, NotFoundError


class ApplicationRepositorySQLAlchemy(ApplicationRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, application) -> ApplicationModel:
        async with self.session_factory() as session:
            db_obj = ApplicationModel.from_domain(application)
            session.add(db_obj)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ConflictError(
                    message="Application conflict (duplicate or FK error)",
                    details=[
                        {
                            "field": "candidate_profile_id|offer_id",
                            "reason": "duplicate or missing FK",
                        }
                    ],
                )
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def get_by_id(self, id: UUID) -> Optional[ApplicationModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ApplicationModel).where(
                    ApplicationModel.id == id, ApplicationModel.deleted_at.is_(None)
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def get_by_candidate_and_offer(
        self, candidate_profile_id: UUID, offer_id: UUID
    ) -> Optional[ApplicationModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ApplicationModel).where(
                    ApplicationModel.candidate_profile_id == candidate_profile_id,
                    ApplicationModel.offer_id == offer_id,
                    ApplicationModel.deleted_at.is_(None),
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def list_by_candidate_profile(
        self, candidate_profile_id: UUID, limit: int = 20, offset: int = 0
    ) -> List[ApplicationModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ApplicationModel)
                .where(
                    ApplicationModel.candidate_profile_id == candidate_profile_id,
                    ApplicationModel.deleted_at.is_(None),
                )
                .offset(offset)
                .limit(limit)
            )
            return [row.to_domain() for row in result.scalars().all()]

    async def update(self, application) -> ApplicationModel:
        async with self.session_factory() as session:
            db_obj = await session.get(ApplicationModel, application.id)
            if not db_obj or db_obj.deleted_at:
                return None
            db_obj.update_from_domain(application)
            db_obj.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def soft_delete(
        self, id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ) -> None:
        async with self.session_factory() as session:
            db_obj = await session.get(ApplicationModel, id)
            if db_obj and not db_obj.deleted_at:
                db_obj.deleted_at = datetime.utcnow()
                db_obj.deleted_by = deleted_by
                db_obj.deletion_reason = reason
                await session.commit()
