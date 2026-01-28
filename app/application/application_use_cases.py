from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.domain.application import Application
from app.domain.application_repository import ApplicationRepository
from app.domain.offer_repository import OfferRepository
from app.domain.candidate_profile_repository import CandidateProfileRepository
from app.domain.errors import ValidationError, NotFoundError, ConflictError


class CreateApplication:
    def __init__(
        self,
        repo: ApplicationRepository,
        offer_repo: OfferRepository,
        profile_repo: CandidateProfileRepository,
    ):
        self.repo = repo
        self.offer_repo = offer_repo
        self.profile_repo = profile_repo

    async def execute(self, candidate_profile_id: UUID, offer_id: UUID) -> Application:
        # validate offer exists and not expired
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundError(
                message="Offer not found",
                details=[{"field": "offer_id", "reason": "not found"}],
            )
        # check deadline
        if (
            hasattr(offer, "application_deadline")
            and offer.application_deadline <= datetime.utcnow()
        ):
            raise ValidationError(
                message="Offer expired or deadline passed",
                details=[{"field": "offer_id", "reason": "expired"}],
            )
        # validate candidate profile exists
        profile = await self.profile_repo.get_by_id(candidate_profile_id)
        if not profile:
            raise NotFoundError(
                message="CandidateProfile not found",
                details=[{"field": "candidate_profile_id", "reason": "not found"}],
            )
        # uniqueness check
        existing = await self.repo.get_by_candidate_and_offer(
            candidate_profile_id, offer_id
        )
        if existing:
            raise ConflictError(
                message="Application already exists",
                details=[
                    {"field": "candidate_profile_id,offer_id", "reason": "duplicate"}
                ],
            )

        application = Application(
            candidate_profile_id=candidate_profile_id, offer_id=offer_id
        )
        return await self.repo.create(application)


class GetApplicationById:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def execute(self, id: UUID) -> Optional[Application]:
        return await self.repo.get_by_id(id)


class ListApplicationsByCandidate:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def execute(
        self, candidate_profile_id: UUID, limit: int = 20, offset: int = 0
    ) -> List[Application]:
        return await self.repo.list_by_candidate_profile(
            candidate_profile_id, limit=limit, offset=offset
        )


class UpdateApplication:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def execute(self, application: Application) -> Application:
        current = await self.repo.get_by_id(application.id)
        if not current:
            raise NotFoundError(
                message="Application not found",
                details=[{"field": "id", "reason": "not found"}],
            )
        return await self.repo.update(application)


class DeleteApplication:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def execute(self, id: UUID, deleted_by: UUID, reason: Optional[str] = None):
        return await self.repo.soft_delete(id, deleted_by, reason)
