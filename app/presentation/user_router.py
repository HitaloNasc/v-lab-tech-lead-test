from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user_use_cases import (
    CreateUser,
    DeleteUser,
    GetUserById,
    UpdateUser,
)
from app.infrastructure.db import get_db
from app.infrastructure.repositories.institution_repository_sqlalchemy import (
    InstitutionRepositorySQLAlchemy,
)
from app.infrastructure.repositories.user_repository_sqlalchemy import (
    UserRepositorySQLAlchemy,
)
from app.presentation.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


# @router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
# async def create_user(
#     user_in: UserCreate,
#     repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
#     inst_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
# ):
#     use_case = CreateUser(repo, inst_repo)
#     user = await use_case.execute(
#         email=user_in.email,
#         password=user_in.password,
#         full_name=user_in.full_name,
#         roles=user_in.roles,
#         institution_id=user_in.institution_id,
#     )
#     return UserRead.from_domain(user)


# @router.get("/{user_id}", response_model=UserRead)
# async def get_user(
#     user_id: UUID, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)
# ):
#     use_case = GetUserById(repo)
#     user = await use_case.execute(user_id)
#     if not user:
#         from app.domain.errors import NotFoundError

#         raise NotFoundError(
#             message="User not found", details=[{"field": "id", "reason": "not found"}]
#         )
#     return UserRead.from_domain(user)


# @router.put("/{user_id}", response_model=UserRead)
# async def update_user(
#     user_id: UUID,
#     user_in: UserUpdate,
#     repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
#     inst_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
# ):
#     use_case = UpdateUser(repo, inst_repo)
#     user = await repo.get_by_id(user_id)
#     if not user:
#         from app.domain.errors import NotFoundError

#         raise NotFoundError(
#             message="User not found", details=[{"field": "id", "reason": "not found"}]
#         )
#     for field, value in user_in.dict(exclude_unset=True).items():
#         if field == "password" and value:
#             # set hashed_password directly
#             from app.infrastructure.security import hash_password

#             user.hashed_password = hash_password(value)
#         elif field == "roles" and value is not None:
#             user.roles = value
#         else:
#             setattr(user, field, value)
#     updated = await use_case.execute(user)
#     return UserRead.from_domain(updated)


# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: UUID,
#     deleted_by: UUID,
#     repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
# ):
#     use_case = DeleteUser(repo)
#     await use_case.execute(user_id, deleted_by)
#     return None
