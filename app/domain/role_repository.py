from typing import List, Optional
from uuid import UUID

from app.domain.role import Role


class RoleRepository:
    async def create(self, role: Role) -> Role:
        raise NotImplementedError()

    async def get_by_id(self, id: UUID) -> Optional[Role]:
        raise NotImplementedError()

    async def get_by_name(self, name: str) -> Optional[Role]:
        raise NotImplementedError()

    async def list(self, limit: int = 20, offset: int = 0) -> List[Role]:
        raise NotImplementedError()

    async def delete(self, id: UUID) -> None:
        raise NotImplementedError()
