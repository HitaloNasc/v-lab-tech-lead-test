from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.domain.candidate_profile_repository import CandidateProfileRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import CandidateProfileModel
from datetime import datetime
from app.domain.errors import ConflictError, NotFoundError


class CandidateProfileRepositorySQLAlchemy(CandidateProfileRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, profile: CandidateProfileModel) -> CandidateProfileModel:
        async with self.session_factory() as session:
            db_obj = CandidateProfileModel.from_domain(profile)
            session.add(db_obj)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ConflictError(
                    message="CandidateProfile conflict",
                    details=[
                        {"field": "user_id", "reason": "duplicate or foreign key error"}
                    ],
                )
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def get_by_id(self, id: UUID) -> Optional[CandidateProfileModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(CandidateProfileModel).where(
                    CandidateProfileModel.id == id,
                    CandidateProfileModel.deleted_at.is_(None),
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def get_by_user_id(self, user_id: UUID) -> Optional[CandidateProfileModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(CandidateProfileModel).where(
                    CandidateProfileModel.user_id == user_id,
                    CandidateProfileModel.deleted_at.is_(None),
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def update(self, profile: CandidateProfileModel) -> CandidateProfileModel:
        async with self.session_factory() as session:
            db_obj = await session.get(CandidateProfileModel, profile.id)
            if not db_obj or db_obj.deleted_at:
                return None
            db_obj.update_from_domain(profile)
            db_obj.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def soft_delete(
        self, id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ) -> None:
        async with self.session_factory() as session:
            db_obj = await session.get(CandidateProfileModel, id)
            if db_obj and not db_obj.deleted_at:
                db_obj.deleted_at = datetime.utcnow()
                db_obj.deleted_by = deleted_by
                db_obj.deletion_reason = reason
                await session.commit()

    async def list(
        self, limit: int = 20, offset: int = 0
    ) -> List[CandidateProfileModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(CandidateProfileModel)
                .where(CandidateProfileModel.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            )
            return [row.to_domain() for row in result.scalars().all()]
