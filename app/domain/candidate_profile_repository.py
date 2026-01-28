from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.candidate_profile import CandidateProfile


class CandidateProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: CandidateProfile) -> CandidateProfile:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[CandidateProfile]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[CandidateProfile]:
        pass

    @abstractmethod
    async def update(self, profile: CandidateProfile) -> CandidateProfile:
        pass

    @abstractmethod
    async def soft_delete(
        self, id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def list(self, limit: int = 20, offset: int = 0) -> List[CandidateProfile]:
        pass
