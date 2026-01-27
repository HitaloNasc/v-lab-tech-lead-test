from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from app.domain.program import Program
from app.domain.program_repository import ProgramRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import ProgramModel
from datetime import datetime


class ProgramRepositorySQLAlchemy(ProgramRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, program: Program) -> Program:
        async with self.session_factory() as session:
            db_obj = ProgramModel.from_domain(program)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def list(self, institution_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[Program]:
        async with self.session_factory() as session:
            query = select(ProgramModel).where(ProgramModel.deleted_at.is_(None))
            if institution_id:
                query = query.where(ProgramModel.institution_id == institution_id)
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return [row.to_domain() for row in result.scalars().all()]

    async def get_by_id(self, program_id: UUID) -> Optional[Program]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ProgramModel).where(ProgramModel.id == program_id, ProgramModel.deleted_at.is_(None))
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def update(self, program: Program) -> Program:
        async with self.session_factory() as session:
            db_obj = await session.get(ProgramModel, program.id)
            if not db_obj or db_obj.deleted_at:
                return None
            db_obj.update_from_domain(program)
            db_obj.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def soft_delete(self, program_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        async with self.session_factory() as session:
            db_obj = await session.get(ProgramModel, program_id)
            if db_obj and not db_obj.deleted_at:
                db_obj.deleted_at = datetime.utcnow()
                db_obj.deleted_by = deleted_by
                db_obj.deletion_reason = reason
                await session.commit()
