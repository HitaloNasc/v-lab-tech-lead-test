from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def soft_delete(self, user_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        pass
