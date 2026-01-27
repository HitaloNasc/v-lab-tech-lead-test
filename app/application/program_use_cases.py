from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.domain.program import Program
from app.domain.program_repository import ProgramRepository
from app.domain.errors import NotFoundError


class CreateProgram:
    def __init__(self, repo: ProgramRepository):
        self.repo = repo

    async def execute(self, institution_id: UUID, name: str, description: Optional[str] = None) -> Program:
        program = Program(institution_id=institution_id, name=name, description=description)
        return await self.repo.create(program)


class ListPrograms:
    def __init__(self, repo: ProgramRepository):
        self.repo = repo

    async def execute(self, institution_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[Program]:
        return await self.repo.list(institution_id=institution_id, limit=limit, offset=offset)


class GetProgramById:
    def __init__(self, repo: ProgramRepository):
        self.repo = repo

    async def execute(self, program_id: UUID) -> Optional[Program]:
        return await self.repo.get_by_id(program_id)


class UpdateProgram:
    def __init__(self, repo: ProgramRepository):
        self.repo = repo

    async def execute(self, program: Program) -> Program:
        current = await self.repo.get_by_id(program.id)
        if not current:
            raise NotFoundError(message="Program not found", details=[{"field": "id", "reason": "not found"}])
        return await self.repo.update(program)


class DeleteProgram:
    def __init__(self, repo: ProgramRepository):
        self.repo = repo

    async def execute(self, program_id: UUID, deleted_by: UUID, reason: Optional[str] = None):
        return await self.repo.soft_delete(program_id, deleted_by, reason)
