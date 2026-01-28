from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.domain.institution import Institution
from app.domain.institution_repository import InstitutionRepository
from app.domain.errors import NotFoundError


class CreateInstitution:
    def __init__(self, repo: InstitutionRepository):
        self.repo = repo

    async def execute(
        self, name: str, description: Optional[str] = None
    ) -> Institution:
        institution = Institution(name=name, description=description)
        return await self.repo.create(institution)


class ListInstitutions:
    def __init__(self, repo: InstitutionRepository):
        self.repo = repo

    async def execute(
        self, name: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Institution]:
        return await self.repo.list(name=name, limit=limit, offset=offset)


class GetInstitutionById:
    def __init__(self, repo: InstitutionRepository):
        self.repo = repo

    async def execute(self, institution_id: UUID) -> Optional[Institution]:
        return await self.repo.get_by_id(institution_id)


class UpdateInstitution:
    def __init__(self, repo: InstitutionRepository):
        self.repo = repo

    async def execute(self, institution: Institution) -> Institution:
        current = await self.repo.get_by_id(institution.id)
        if not current:
            raise NotFoundError(
                message="Institution not found",
                details=[{"field": "id", "reason": "not found"}],
            )
        # basic update
        return await self.repo.update(institution)


class DeleteInstitution:
    def __init__(self, repo: InstitutionRepository):
        self.repo = repo

    async def execute(
        self, institution_id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ):
        return await self.repo.soft_delete(institution_id, deleted_by, reason)
