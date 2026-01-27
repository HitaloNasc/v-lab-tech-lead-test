from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from app.domain.institution_repository import InstitutionRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import InstitutionModel
from datetime import datetime


class InstitutionRepositorySQLAlchemy(InstitutionRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, institution) -> InstitutionModel:
        async with self.session_factory() as session:
            db_inst = InstitutionModel.from_domain(institution)
            session.add(db_inst)
            await session.commit()
            await session.refresh(db_inst)
            return db_inst.to_domain()

    async def list(self, name: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[InstitutionModel]:
        async with self.session_factory() as session:
            query = select(InstitutionModel).where(InstitutionModel.deleted_at.is_(None))
            if name:
                query = query.where(InstitutionModel.name.ilike(f"%{name}%"))
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return [row.to_domain() for row in result.scalars().all()]

    async def get_by_id(self, institution_id: UUID) -> Optional[InstitutionModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstitutionModel).where(InstitutionModel.id == institution_id, InstitutionModel.deleted_at.is_(None))
            )
            db_inst = result.scalar_one_or_none()
            return db_inst.to_domain() if db_inst else None

    async def update(self, institution) -> InstitutionModel:
        async with self.session_factory() as session:
            db_inst = await session.get(InstitutionModel, institution.id)
            if not db_inst or db_inst.deleted_at:
                return None
            db_inst.update_from_domain(institution)
            db_inst.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_inst)
            return db_inst.to_domain()

    async def soft_delete(self, institution_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        async with self.session_factory() as session:
            db_inst = await session.get(InstitutionModel, institution_id)
            if db_inst and not db_inst.deleted_at:
                db_inst.deleted_at = datetime.utcnow()
                db_inst.deleted_by = deleted_by
                db_inst.deletion_reason = reason
                await session.commit()