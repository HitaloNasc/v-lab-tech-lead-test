from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID
from app.infrastructure.repositories.institution_repository_sqlalchemy import InstitutionRepositorySQLAlchemy
from app.application.institution_use_cases import (
    CreateInstitution, ListInstitutions, GetInstitutionById, UpdateInstitution, DeleteInstitution
)
from app.infrastructure.db import get_db
from app.presentation.schemas import InstitutionCreate, InstitutionRead, InstitutionUpdate
from app.domain.institution import Institution
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/institutions", tags=["institutions"])


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


@router.post("/", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
async def create_institution(
    inst_in: InstitutionCreate,
    repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = CreateInstitution(repo)
    inst = await use_case.execute(**inst_in.dict())
    return InstitutionRead.from_domain(inst)


@router.get("/", response_model=List[InstitutionRead])
async def list_institutions(
    name: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = ListInstitutions(repo)
    items = await use_case.execute(name=name, limit=limit, offset=offset)
    return [InstitutionRead.from_domain(i) for i in items]


@router.get("/{institution_id}", response_model=InstitutionRead)
async def get_institution_by_id(
    institution_id: UUID,
    repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = GetInstitutionById(repo)
    inst = await use_case.execute(institution_id)
    if not inst:
        from app.domain.errors import NotFoundError
        raise NotFoundError(message="Institution not found", details=[{"field": "id", "reason": "not found"}])
    return InstitutionRead.from_domain(inst)


@router.put("/{institution_id}", response_model=InstitutionRead)
async def update_institution(
    institution_id: UUID,
    inst_in: InstitutionUpdate,
    repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = UpdateInstitution(repo)
    inst = await repo.get_by_id(institution_id)
    if not inst:
        from app.domain.errors import NotFoundError
        raise NotFoundError(message="Institution not found", details=[{"field": "id", "reason": "not found"}])
    for field, value in inst_in.dict(exclude_unset=True).items():
        setattr(inst, field, value)
    updated = await use_case.execute(inst)
    return InstitutionRead.from_domain(updated)


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: UUID,
    deleted_by: UUID,
    reason: Optional[str] = None,
    repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = DeleteInstitution(repo)
    await use_case.execute(institution_id, deleted_by, reason)
    return None
