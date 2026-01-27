from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.program import Program


class ProgramRepository(ABC):
    @abstractmethod
    async def create(self, program: Program) -> Program:
        pass

    @abstractmethod
    async def list(self, institution_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[Program]:
        pass

    @abstractmethod
    async def get_by_id(self, program_id: UUID) -> Optional[Program]:
        pass

    @abstractmethod
    async def update(self, program: Program) -> Program:
        pass

    @abstractmethod
    async def soft_delete(self, program_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        pass
