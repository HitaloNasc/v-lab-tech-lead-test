from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from app.infrastructure.repositories.application_repository_sqlalchemy import (
    ApplicationRepositorySQLAlchemy,
)
from app.infrastructure.repositories.offer_repository_sqlalchemy import (
    OfferRepositorySQLAlchemy,
)
from app.infrastructure.repositories.candidate_profile_repository_sqlalchemy import (
    CandidateProfileRepositorySQLAlchemy,
)
from app.application.application_use_cases import (
    CreateApplication,
    GetApplicationById,
    ListApplicationsByCandidate,
    UpdateApplication,
    DeleteApplication,
)
from app.infrastructure.db import get_db
from app.presentation.schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.errors import NotFoundError

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


def get_application_repo(db: AsyncSession = Depends(get_db)):
    return ApplicationRepositorySQLAlchemy(lambda: db)


def get_offer_repo(db: AsyncSession = Depends(get_db)):
    return OfferRepositorySQLAlchemy(lambda: db)


def get_profile_repo(db: AsyncSession = Depends(get_db)):
    return CandidateProfileRepositorySQLAlchemy(lambda: db)


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_in: ApplicationCreate,
    app_repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
    offer_repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
    profile_repo: CandidateProfileRepositorySQLAlchemy = Depends(get_profile_repo),
):
    use_case = CreateApplication(app_repo, offer_repo, profile_repo)
    application = await use_case.execute(app_in.candidate_profile_id, app_in.offer_id)
    return ApplicationRead.from_domain(application)


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: UUID,
    repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
):
    use_case = GetApplicationById(repo)
    application = await use_case.execute(application_id)
    if not application:
        raise NotFoundError(
            message="Application not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    return ApplicationRead.from_domain(application)


@router.get(
    "/by-candidate/{candidate_profile_id}", response_model=List[ApplicationRead]
)
async def list_by_candidate(
    candidate_profile_id: UUID,
    limit: int = 20,
    offset: int = 0,
    repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
):
    use_case = ListApplicationsByCandidate(repo)
    apps = await use_case.execute(candidate_profile_id, limit=limit, offset=offset)
    return [ApplicationRead.from_domain(a) for a in apps]


@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: UUID,
    app_in: ApplicationUpdate,
    repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
):
    use_case = UpdateApplication(repo)
    application = await repo.get_by_id(application_id)
    if not application:
        raise NotFoundError(
            message="Application not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    for field, value in app_in.dict(exclude_unset=True).items():
        setattr(application, field, value)
    updated = await use_case.execute(application)
    return ApplicationRead.from_domain(updated)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    deleted_by: UUID,
    repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
):
    use_case = DeleteApplication(repo)
    await use_case.execute(application_id, deleted_by)
    return None
