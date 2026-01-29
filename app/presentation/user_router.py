from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user_use_cases import (
    CreateUser,
    DeleteUser,
    GetUserById,
    UpdateUser,
)
from app.domain.errors import ForbiddenError, NotFoundError
from app.infrastructure.db import get_db
from app.infrastructure.repositories.application_repository_sqlalchemy import (
    ApplicationRepositorySQLAlchemy,
)
from app.infrastructure.repositories.candidate_profile_repository_sqlalchemy import (
    CandidateProfileRepositorySQLAlchemy,
)
from app.infrastructure.repositories.institution_repository_sqlalchemy import (
    InstitutionRepositorySQLAlchemy,
)
from app.infrastructure.repositories.user_repository_sqlalchemy import (
    UserRepositorySQLAlchemy,
)
from app.presentation.auth_decorators import require_auth, require_roles
from app.presentation.schemas import ApplicationRead, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


def get_application_repo(db: AsyncSession = Depends(get_db)):
    return ApplicationRepositorySQLAlchemy(lambda: db)


def get_profile_repo(db: AsyncSession = Depends(get_db)):
    return CandidateProfileRepositorySQLAlchemy(lambda: db)


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


@router.put("/{user_id}", response_model=UserRead)
@require_auth
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
    inst_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
    profile_repo: CandidateProfileRepositorySQLAlchemy = Depends(get_profile_repo),
    request: Request = None,
):
    use_case = UpdateUser(repo, inst_repo, profile_repo)

    requester = getattr(request.state, "user", None)
    if not requester:
        raise ForbiddenError(message="Not authenticated")

    updates = user_in.dict(exclude_unset=True)

    updated = await use_case.execute(
        user_id=user_id,
        updates=updates,
        requester_id=getattr(requester, "id"),
        requester_roles=getattr(requester, "roles", []),
    )

    return UserRead.from_domain(updated)


# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: UUID,
#     deleted_by: UUID,
#     repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
# ):
#     use_case = DeleteUser(repo)
#     await use_case.execute(user_id, deleted_by)
#     return None


@router.get("/{user_id}/applications", response_model=List[ApplicationRead])
@require_auth
@require_roles("candidate", "sys_admin")
async def list_user_applications(
    user_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    app_repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
    profile_repo: CandidateProfileRepositorySQLAlchemy = Depends(get_profile_repo),
    request: Request = None,
):
    from app.application.application_use_cases import ListApplicationsByCandidate

    user = getattr(request.state, "user", None)
    if not user:
        raise ForbiddenError(message="Not authenticated")

    normalized_roles = [str(r).lower() for r in (getattr(user, "roles", []) or [])]

    # if candidate role, ensure they only request their own data
    if "candidate" in normalized_roles and str(user.id) != str(user_id):
        raise ForbiddenError(
            message="Candidates can only view their own applications",
            details=[{"field": "user_id", "reason": "forbidden"}],
        )

    # map user -> candidate_profile
    profile = await profile_repo.get_by_user_id(user_id)
    if not profile:
        raise NotFoundError(
            message="CandidateProfile not found",
            details=[{"field": "user_id", "reason": "not found"}],
        )

    use_case = ListApplicationsByCandidate(app_repo)
    apps = await use_case.execute(profile.id, limit=limit, offset=offset)
    return [ApplicationRead.from_domain(a) for a in apps]
