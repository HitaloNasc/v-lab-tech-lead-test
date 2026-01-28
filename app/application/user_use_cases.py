from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.user import User
from app.domain.role import Role
from app.domain.user_repository import UserRepository
from app.domain.errors import ValidationError, NotFoundError
from app.infrastructure.security import hash_password, verify_password, create_access_token


class CreateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, email: str, password: str, full_name: Optional[str] = None, roles: Optional[list] = None) -> User:
        # hash password
        hashed = hash_password(password)
        # accept optional roles list (list of role names or Role domain objects)
        roles_objs = None
        if roles:
            roles_objs = [r if hasattr(r, "name") else Role(name=r) for r in roles]
        user = User(email=email, hashed_password=hashed, full_name=full_name, roles=roles_objs)
        return await self.repo.create(user)


class AuthenticateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError(message="User not found", details=[{"field": "email", "reason": "not found"}])
        if not verify_password(password, user.hashed_password):
            raise ValidationError(message="Invalid credentials", details=[{"field": "password", "reason": "invalid"}])
        if not user.is_active:
            raise ValidationError(message="User inactive", details=[{"field": "user", "reason": "inactive"}])
        # include roles as array claim for downstream consumers
        roles_claim = []
        if hasattr(user, "roles") and user.roles:
            for r in user.roles:
                try:
                    roles_claim.append(r.name)
                except Exception:
                    continue
        token = create_access_token(str(user.id), extra_claims={"roles": roles_claim})
        return {"access_token": token, "token_type": "bearer", "user": user}


class GetUserById:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, user_id: UUID) -> Optional[User]:
        return await self.repo.get_by_id(user_id)


class UpdateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, user: User) -> User:
        current = await self.repo.get_by_id(user.id)
        if not current:
            raise NotFoundError(message="User not found", details=[{"field": "id", "reason": "not found"}])
        # if password present and plain, caller should set hashed_password before calling repo
        return await self.repo.update(user)


class DeleteUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, user_id: UUID, deleted_by: UUID, reason: Optional[str] = None):
        return await self.repo.soft_delete(user_id, deleted_by, reason)
