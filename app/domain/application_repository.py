from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.application import Application


class ApplicationRepository(ABC):
    @abstractmethod
    async def create(self, application: Application) -> Application:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Application]:
        pass

    @abstractmethod
    async def get_by_candidate_and_offer(self, candidate_profile_id: UUID, offer_id: UUID) -> Optional[Application]:
        pass

    @abstractmethod
    async def list_by_candidate_profile(self, candidate_profile_id: UUID, limit: int = 20, offset: int = 0) -> List[Application]:
        pass

    @abstractmethod
    async def update(self, application: Application) -> Application:
        pass

    @abstractmethod
    async def soft_delete(self, id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        pass
