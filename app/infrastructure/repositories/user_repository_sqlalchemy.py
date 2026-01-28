from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.domain.user import User
from app.domain.user_repository import UserRepository
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories.sqlalchemy_models import UserModel
from app.infrastructure.repositories.sqlalchemy_models import RoleModel, UserRoleModel
from app.domain.role import Role as RoleDomain
from datetime import datetime
from app.domain.errors import ConflictError, NotFoundError


class UserRepositorySQLAlchemy(UserRepository):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    async def create(self, user: User) -> User:
        async with self.session_factory() as session:
            db_obj = UserModel.from_domain(user)
            session.add(db_obj)
            try:
                # flush to persist the user and generate any DB-side defaults/ids
                await session.flush()
            except IntegrityError:
                await session.rollback()
                raise ConflictError(
                    message="Email already exists",
                    details=[{"field": "email", "reason": "duplicate"}],
                )

            # handle roles associations if provided on domain object
            if hasattr(user, "roles") and user.roles:
                for r in user.roles:
                    role_name = r.name if hasattr(r, "name") else str(r)
                    result = await session.execute(
                        select(RoleModel).where(
                            RoleModel.name == role_name, RoleModel.deleted_at.is_(None)
                        )
                    )
                    role_db = result.scalar_one_or_none()
                    if not role_db:
                        # create role if it doesn't exist
                        role_db = RoleModel.from_domain(RoleDomain(name=role_name))
                        session.add(role_db)
                        await session.flush()
                    # create association row explicitly to avoid touching
                    # potential lazy-loaded collection on `db_obj.roles`
                    session.add(UserRoleModel(user_id=db_obj.id, role_id=role_db.id))

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ConflictError(
                    message="Email already exists",
                    details=[{"field": "email", "reason": "duplicate"}],
                )

            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = (
                select(UserModel)
                .where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
                .options(
                    selectinload(UserModel.user_roles).selectinload(UserRoleModel.role)
                )
            )
            result = await session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = (
                select(UserModel)
                .where(UserModel.email == email, UserModel.deleted_at.is_(None))
                .options(
                    selectinload(UserModel.user_roles).selectinload(UserRoleModel.role)
                )
            )
            result = await session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            return db_obj.to_domain() if db_obj else None

    async def update(self, user: User) -> User:
        async with self.session_factory() as session:
            db_obj = await session.get(UserModel, user.id)
            if not db_obj or db_obj.deleted_at:
                return None
            db_obj.update_from_domain(user)
            # sync roles if provided
            if hasattr(user, "roles"):
                # delete existing association rows for this user and add new ones
                await session.execute(
                    delete(UserRoleModel).where(UserRoleModel.user_id == db_obj.id)
                )
                for r in user.roles:
                    role_name = r.name if hasattr(r, "name") else str(r)
                    result = await session.execute(
                        select(RoleModel).where(
                            RoleModel.name == role_name, RoleModel.deleted_at.is_(None)
                        )
                    )
                    role_db = result.scalar_one_or_none()
                    if not role_db:
                        role_db = RoleModel.from_domain(RoleDomain(name=role_name))
                        session.add(role_db)
                        await session.flush()
                    session.add(UserRoleModel(user_id=db_obj.id, role_id=role_db.id))

            db_obj.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_obj)
            return db_obj.to_domain()

    async def soft_delete(
        self, user_id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ) -> None:
        async with self.session_factory() as session:
            db_obj = await session.get(UserModel, user_id)
            if db_obj and not db_obj.deleted_at:
                db_obj.deleted_at = datetime.utcnow()
                db_obj.deleted_by = deleted_by
                db_obj.deletion_reason = reason
                await session.commit()

    async def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .where(UserModel.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            )
            return [row.to_domain() for row in result.scalars().all()]
