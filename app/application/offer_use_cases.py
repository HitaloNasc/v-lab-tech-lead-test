from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.offer import Offer, OfferStatus, OfferType
from app.domain.offer_repository import OfferRepository
from app.domain.institution_repository import InstitutionRepository
from app.domain.program_repository import ProgramRepository
from app.domain.errors import ValidationError, NotFoundError


class CreateOffer:
    def __init__(self, repo: OfferRepository, institution_repo: InstitutionRepository, program_repo: ProgramRepository):
        self.repo = repo
        self.institution_repo = institution_repo
        self.program_repo = program_repo

    async def execute(
        self,
        institution_id: UUID,
        title: str,
        description: str,
        type: OfferType,
        publication_date: datetime,
        application_deadline: datetime,
        program_id: Optional[UUID] = None,
    ) -> Offer:
        if application_deadline <= publication_date:
            raise ValidationError(
                message="application_deadline must be after publication_date",
                details=[
                    {
                        "field": "application_deadline",
                        "reason": "must be after publication_date",
                    }
                ],
            )

        # validate institution exists
        inst = await self.institution_repo.get_by_id(institution_id)
        if not inst:
            raise NotFoundError(message="Institution not found", details=[{"field": "institution_id", "reason": "not found"}])

        # validate program if provided
        if program_id:
            prog = await self.program_repo.get_by_id(program_id)
            if not prog:
                raise NotFoundError(message="Program not found", details=[{"field": "program_id", "reason": "not found"}])

        offer = Offer(
            institution_id=institution_id,
            program_id=program_id,
            title=title,
            description=description,
            type=type,
            status=OfferStatus.DRAFT,
            publication_date=publication_date,
            application_deadline=application_deadline,
        )
        return await self.repo.create(offer)


class ListOffers:
    def __init__(self, repo: OfferRepository):
        self.repo = repo

    async def execute(
        self,
        institution_id: Optional[UUID] = None,
        type: Optional[OfferType] = None,
        status: Optional[OfferStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        return await self.repo.list(
            institution_id=institution_id,
            type=type,
            status=status,
            limit=limit,
            offset=offset,
        )


class GetOfferById:
    def __init__(self, repo: OfferRepository):
        self.repo = repo

    async def execute(self, offer_id: UUID) -> Optional[Offer]:
        return await self.repo.get_by_id(offer_id)


class UpdateOffer:
    def __init__(self, repo: OfferRepository):
        self.repo = repo

    async def execute(self, offer: Offer) -> Offer:
        # Buscar registro atual
        current = await self.repo.get_by_id(offer.id)
        if not current:
            raise NotFoundError(
                message="Offer not found",
                details=[{"field": "id", "reason": "not found"}],
            )
        # Verifica se algum dos campos foi alterado
        pub_changed = offer.publication_date and offer.publication_date != current.publication_date
        deadline_changed = offer.application_deadline and offer.application_deadline != current.application_deadline
        if pub_changed or deadline_changed:
            pub = offer.publication_date or current.publication_date
            deadline = offer.application_deadline or current.application_deadline
            if deadline <= pub:
                raise ValidationError(
                    message="application_deadline must be after publication_date",
                    details=[
                        {
                            "field": "application_deadline",
                            "reason": "must be after publication_date",
                        }
                    ],
                )
        return await self.repo.update(offer)


class DeleteOffer:
    def __init__(self, repo: OfferRepository):
        self.repo = repo

    async def execute(
        self, offer_id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ):
        return await self.repo.soft_delete(offer_id, deleted_by, reason)
