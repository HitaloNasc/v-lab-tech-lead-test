from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.offer_use_cases import (
    CreateOffer,
    DeleteOffer,
    GetOfferById,
    ListOffers,
    UpdateOffer,
)
from app.domain.offer import OfferStatus, OfferType
from app.infrastructure.db import get_db
from app.infrastructure.repositories.institution_repository_sqlalchemy import (
    InstitutionRepositorySQLAlchemy,
)
from app.infrastructure.repositories.offer_repository_sqlalchemy import (
    OfferRepositorySQLAlchemy,
)
from app.infrastructure.repositories.application_repository_sqlalchemy import (
    ApplicationRepositorySQLAlchemy,
)
from app.infrastructure.repositories.user_repository_sqlalchemy import (
    UserRepositorySQLAlchemy,
)
from app.infrastructure.repositories.program_repository_sqlalchemy import (
    ProgramRepositorySQLAlchemy,
)
from app.presentation.auth_decorators import require_auth, require_roles
from app.presentation.schemas import (
    ApplicationRead,
    OfferCreate,
    OfferRead,
    OfferUpdate,
)

router = APIRouter(prefix="/api/v1/offers", tags=["offers"])


def get_offer_repo(db: AsyncSession = Depends(get_db)):
    return OfferRepositorySQLAlchemy(lambda: db)


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


def get_program_repo(db: AsyncSession = Depends(get_db)):
    return ProgramRepositorySQLAlchemy(lambda: db)


def get_application_repo(db: AsyncSession = Depends(get_db)):
    return ApplicationRepositorySQLAlchemy(lambda: db)


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


@router.post("/", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
@require_auth
@require_roles("institution_admin", "sys_admin")
async def create_offer(
    offer_in: OfferCreate,
    repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
    inst_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
    prog_repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
):
    use_case = CreateOffer(repo, inst_repo, prog_repo)
    offer = await use_case.execute(**offer_in.dict())
    return OfferRead.from_domain(offer)


@router.get("/", response_model=List[OfferRead])
async def list_offers(
    institution_id: Optional[UUID] = Query(None),
    type: Optional[OfferType] = Query(None),
    status_: Optional[OfferStatus] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
):
    use_case = ListOffers(repo)
    offers = await use_case.execute(
        institution_id=institution_id,
        type=type,
        status=status_,
        limit=limit,
        offset=offset,
    )
    return [OfferRead.from_domain(o) for o in offers]


@router.get("/{offer_id}", response_model=OfferRead)
async def get_offer_by_id(
    offer_id: UUID,
    repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
):
    use_case = GetOfferById(repo)
    offer = await use_case.execute(offer_id)
    if not offer:
        from app.domain.errors import NotFoundError

        raise NotFoundError(
            message="Offer not found", details=[{"field": "id", "reason": "not found"}]
        )
    return OfferRead.from_domain(offer)


@router.get("/{offer_id}/applications", response_model=List[ApplicationRead])
@require_auth
@require_roles("institution_admin", "sys_admin")
async def list_applications_for_offer(
    offer_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    app_repo: ApplicationRepositorySQLAlchemy = Depends(get_application_repo),
    offer_repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
    user_repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
    request: Request = None,
):
    from app.application.application_use_cases import ListApplicationsByOffer

    # request.state.user is attached by the auth decorator
    user = getattr(request.state, "user", None)
    requester_id = UUID(str(getattr(user, "id")))
    requester_roles = getattr(user, "roles", [])

    use_case = ListApplicationsByOffer(app_repo, offer_repo, user_repo)
    apps = await use_case.execute(
        offer_id, requester_id, requester_roles, limit=limit, offset=offset
    )
    from app.presentation.schemas import ApplicationRead

    return [ApplicationRead.from_domain(a) for a in apps]


@router.put("/{offer_id}", response_model=OfferRead)
@require_auth
@require_roles("institution_admin", "sys_admin")
async def update_offer(
    offer_id: UUID,
    offer_in: OfferUpdate,
    repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
):
    use_case = UpdateOffer(repo)
    offer = await repo.get_by_id(offer_id)
    if not offer:
        from app.domain.errors import NotFoundError

        raise NotFoundError(
            message="Offer not found", details=[{"field": "id", "reason": "not found"}]
        )
    for field, value in offer_in.dict(exclude_unset=True).items():
        setattr(offer, field, value)
    updated = await use_case.execute(offer)
    return OfferRead.from_domain(updated)


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_auth
@require_roles("institution_admin", "sys_admin")
async def delete_offer(
    offer_id: UUID,
    deleted_by: UUID,
    reason: Optional[str] = None,
    repo: OfferRepositorySQLAlchemy = Depends(get_offer_repo),
):
    use_case = DeleteOffer(repo)
    await use_case.execute(offer_id, deleted_by, reason)
    return None
