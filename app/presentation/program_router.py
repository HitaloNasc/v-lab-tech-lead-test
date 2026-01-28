from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID
from app.infrastructure.repositories.program_repository_sqlalchemy import (
    ProgramRepositorySQLAlchemy,
)
from app.infrastructure.repositories.institution_repository_sqlalchemy import (
    InstitutionRepositorySQLAlchemy,
)
from app.application.program_use_cases import (
    CreateProgram,
    ListPrograms,
    GetProgramById,
    UpdateProgram,
    DeleteProgram,
)
from app.infrastructure.db import get_db
from app.presentation.schemas import ProgramCreate, ProgramRead, ProgramUpdate
from app.domain.program import Program
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/programs", tags=["programs"])


def get_program_repo(db: AsyncSession = Depends(get_db)):
    return ProgramRepositorySQLAlchemy(lambda: db)


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


@router.post("/", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: ProgramCreate,
    repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
    inst_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
):
    use_case = CreateProgram(repo, inst_repo)
    program = await use_case.execute(**payload.dict())
    return ProgramRead.from_domain(program)


@router.get("/", response_model=List[ProgramRead])
async def list_programs(
    institution_id: Optional[UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
):
    use_case = ListPrograms(repo)
    items = await use_case.execute(
        institution_id=institution_id, limit=limit, offset=offset
    )
    return [ProgramRead.from_domain(i) for i in items]


@router.get("/{program_id}", response_model=ProgramRead)
async def get_program_by_id(
    program_id: UUID,
    repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
):
    use_case = GetProgramById(repo)
    item = await use_case.execute(program_id)
    if not item:
        from app.domain.errors import NotFoundError

        raise NotFoundError(
            message="Program not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    return ProgramRead.from_domain(item)


@router.put("/{program_id}", response_model=ProgramRead)
async def update_program(
    program_id: UUID,
    payload: ProgramUpdate,
    repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
):
    use_case = UpdateProgram(repo)
    program = await repo.get_by_id(program_id)
    if not program:
        from app.domain.errors import NotFoundError

        raise NotFoundError(
            message="Program not found",
            details=[{"field": "id", "reason": "not found"}],
        )
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(program, field, value)
    updated = await use_case.execute(program)
    return ProgramRead.from_domain(updated)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: UUID,
    deleted_by: UUID,
    reason: Optional[str] = None,
    repo: ProgramRepositorySQLAlchemy = Depends(get_program_repo),
):
    use_case = DeleteProgram(repo)
    await use_case.execute(program_id, deleted_by, reason)
    return None
