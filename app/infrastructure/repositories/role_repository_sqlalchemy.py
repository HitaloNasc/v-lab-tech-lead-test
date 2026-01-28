from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from app.domain.role_repository import RoleRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import RoleModel
from datetime import datetime


class RoleRepositorySQLAlchemy(RoleRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, role) -> RoleModel:
        async with self.session_factory() as session:
            db_obj = RoleModel.from_domain(role)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def get_by_id(self, id: UUID) -> Optional[RoleModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RoleModel).where(
                    RoleModel.id == id, RoleModel.deleted_at.is_(None)
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RoleModel).where(
                    RoleModel.name == name, RoleModel.deleted_at.is_(None)
                )
            )
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def list(self, limit: int = 20, offset: int = 0) -> List[RoleModel]:
        async with self.session_factory() as session:
            query = (
                select(RoleModel)
                .where(RoleModel.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            return [row.to_domain() for row in result.scalars().all()]

    async def delete(self, id: UUID) -> None:
        async with self.session_factory() as session:
            db_obj = await session.get(RoleModel, id)
            if db_obj and not db_obj.deleted_at:
                db_obj.deleted_at = datetime.utcnow()
                await session.commit()
