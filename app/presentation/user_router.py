from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from app.infrastructure.repositories.user_repository_sqlalchemy import UserRepositorySQLAlchemy
from app.application.user_use_cases import CreateUser, GetUserById, UpdateUser, DeleteUser
from app.infrastructure.db import get_db
from app.presentation.schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)):
    use_case = CreateUser(repo)
    user = await use_case.execute(email=user_in.email, password=user_in.password, full_name=user_in.full_name)
    return UserRead.from_domain(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)):
    use_case = GetUserById(repo)
    user = await use_case.execute(user_id)
    if not user:
        from app.domain.errors import NotFoundError
        raise NotFoundError(message="User not found", details=[{"field": "id", "reason": "not found"}])
    return UserRead.from_domain(user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, user_in: UserUpdate, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)):
    use_case = UpdateUser(repo)
    user = await repo.get_by_id(user_id)
    if not user:
        from app.domain.errors import NotFoundError
        raise NotFoundError(message="User not found", details=[{"field": "id", "reason": "not found"}])
    for field, value in user_in.dict(exclude_unset=True).items():
        if field == 'password' and value:
            # set hashed_password directly
            from app.infrastructure.security import hash_password
            user.hashed_password = hash_password(value)
        else:
            setattr(user, field, value)
    updated = await use_case.execute(user)
    return UserRead.from_domain(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, deleted_by: UUID, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)):
    use_case = DeleteUser(repo)
    await use_case.execute(user_id, deleted_by)
    return None
