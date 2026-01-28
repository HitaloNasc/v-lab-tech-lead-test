from typing import Optional
from uuid import UUID
from app.domain.candidate_profile import CandidateProfile
from app.domain.candidate_profile_repository import CandidateProfileRepository
from app.domain.user_repository import UserRepository
from app.domain.errors import ValidationError, NotFoundError, ConflictError


class CreateCandidateProfile:
    def __init__(self, repo: CandidateProfileRepository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo

    async def execute(self, user_id: UUID, full_name: str, date_of_birth: Optional[str] = None, cpf: Optional[str] = None) -> CandidateProfile:
        # validate user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found", details=[{"field": "user_id", "reason": "not found"}])
        # ensure unique: no existing profile for user
        existing = await self.repo.get_by_user_id(user_id)
        if existing:
            raise ConflictError(message="CandidateProfile already exists for user", details=[{"field": "user_id", "reason": "unique"}])

        profile = CandidateProfile(user_id=user_id, full_name=full_name, date_of_birth=date_of_birth, cpf=cpf)
        return await self.repo.create(profile)


class GetCandidateProfileById:
    def __init__(self, repo: CandidateProfileRepository):
        self.repo = repo

    async def execute(self, id: UUID) -> Optional[CandidateProfile]:
        return await self.repo.get_by_id(id)


class GetCandidateProfileByUserId:
    def __init__(self, repo: CandidateProfileRepository):
        self.repo = repo

    async def execute(self, user_id: UUID) -> Optional[CandidateProfile]:
        return await self.repo.get_by_user_id(user_id)


class UpdateCandidateProfile:
    def __init__(self, repo: CandidateProfileRepository):
        self.repo = repo

    async def execute(self, profile: CandidateProfile) -> CandidateProfile:
        current = await self.repo.get_by_id(profile.id)
        if not current:
            raise NotFoundError(message="CandidateProfile not found", details=[{"field": "id", "reason": "not found"}])
        return await self.repo.update(profile)


class DeleteCandidateProfile:
    def __init__(self, repo: CandidateProfileRepository):
        self.repo = repo

    async def execute(self, id: UUID, deleted_by: UUID, reason: Optional[str] = None):
        return await self.repo.soft_delete(id, deleted_by, reason)
