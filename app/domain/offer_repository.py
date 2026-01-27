from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.offer import Offer, OfferType, OfferStatus

class OfferRepository(ABC):
    @abstractmethod
    async def create(self, offer: Offer) -> Offer:
        pass

    @abstractmethod
    async def list(
        self,
        institution_id: Optional[UUID] = None,
        type: Optional[OfferType] = None,
        status: Optional[OfferStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Offer]:
        pass

    @abstractmethod
    async def get_by_id(self, offer_id: UUID) -> Optional[Offer]:
        pass

    @abstractmethod
    async def update(self, offer: Offer) -> Offer:
        pass

    @abstractmethod
    async def soft_delete(self, offer_id: UUID, deleted_by: UUID, reason: Optional[str] = None) -> None:
        pass
