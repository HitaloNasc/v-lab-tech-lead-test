from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.institution import Institution


class InstitutionRepository(ABC):
    @abstractmethod
    async def create(self, institution: Institution) -> Institution:
        pass

    @abstractmethod
    async def list(self, name: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Institution]:
        pass

    @abstractmethod
    async def get_by_id(self, institution_id: UUID) -> Optional[Institution]:
        pass

    @abstractmethod
    async def update(self, institution: Institution) -> Institution:
        pass

    @abstractmethod
    async def soft_delete(self, institution_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        pass
