from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from app.infrastructure.repositories.candidate_profile_repository_sqlalchemy import (
    CandidateProfileRepositorySQLAlchemy,
)
from app.infrastructure.repositories.user_repository_sqlalchemy import (
    UserRepositorySQLAlchemy,
)
from app.application.candidate_profile_use_cases import (
    CreateCandidateProfile,
    GetCandidateProfileById,
    GetCandidateProfileByUserId,
    UpdateCandidateProfile,
    DeleteCandidateProfile,
)
from app.infrastructure.db import get_db
from app.presentation.schemas import (
    CandidateProfileCreate,
    CandidateProfileRead,
    CandidateProfileUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.errors import NotFoundError

router = APIRouter(prefix="/api/v1/candidate-profiles", tags=["candidate-profiles"])


def get_candidate_repo(db: AsyncSession = Depends(get_db)):
    return CandidateProfileRepositorySQLAlchemy(lambda: db)


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


@router.post(
    "/", response_model=CandidateProfileRead, status_code=status.HTTP_201_CREATED
)
async def create_profile(
    profile_in: CandidateProfileCreate,
    candidate_repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
    user_repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
):
    use_case = CreateCandidateProfile(candidate_repo, user_repo)
    profile = await use_case.execute(
        profile_in.user_id,
        profile_in.full_name,
        profile_in.date_of_birth,
        profile_in.cpf,
    )
    return CandidateProfileRead.from_domain(profile)


@router.get("/{profile_id}", response_model=CandidateProfileRead)
async def get_profile(
    profile_id: UUID,
    repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
):
    use_case = GetCandidateProfileById(repo)
    profile = await use_case.execute(profile_id)
    if not profile:
        raise NotFoundError(
            message="CandidateProfile not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    return CandidateProfileRead.from_domain(profile)


@router.get("/by-user/{user_id}", response_model=CandidateProfileRead)
async def get_profile_by_user(
    user_id: UUID,
    repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
):
    use_case = GetCandidateProfileByUserId(repo)
    profile = await use_case.execute(user_id)
    if not profile:
        raise NotFoundError(
            message="CandidateProfile not found",
            details=[{"field": "user_id", "reason": "not found"}],
        )
    return CandidateProfileRead.from_domain(profile)


@router.put("/{profile_id}", response_model=CandidateProfileRead)
async def update_profile(
    profile_id: UUID,
    profile_in: CandidateProfileUpdate,
    repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
):
    use_case = UpdateCandidateProfile(repo)
    profile = await repo.get_by_id(profile_id)
    if not profile:
        raise NotFoundError(
            message="CandidateProfile not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    for field, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    updated = await use_case.execute(profile)
    return CandidateProfileRead.from_domain(updated)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    deleted_by: UUID,
    repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
):
    use_case = DeleteCandidateProfile(repo)
    await use_case.execute(profile_id, deleted_by)
    return None
