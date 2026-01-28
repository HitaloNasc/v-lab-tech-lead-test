from typing import Optional, List
from uuid import UUID

from app.application.user_use_cases import CreateUser
from app.application.candidate_profile_use_cases import CreateCandidateProfile
from app.domain.user_repository import UserRepository
from app.domain.candidate_profile_repository import CandidateProfileRepository
from app.domain.institution_repository import InstitutionRepository
from app.domain.role_repository import RoleRepository
from app.domain.errors import ValidationError


class RegisterUser:
    def __init__(
        self,
        user_repo: UserRepository,
        institution_repo: InstitutionRepository,
        candidate_repo: CandidateProfileRepository,
        role_repo: RoleRepository,
    ):
        self.user_repo = user_repo
        self.institution_repo = institution_repo
        self.candidate_repo = candidate_repo
        self.role_repo = role_repo

    async def execute(
        self,
        email: str,
        password: str,
        roles: List[str],
        institution_id: Optional[UUID] = None,
        candidate_profile: Optional[dict] = None,
    ):
        # basic roles validation
        if not roles or not isinstance(roles, list):
            raise ValidationError(
                message="roles is required and must be a list",
                details=[{"field": "roles", "reason": "required"}],
            )

        # validate allowed roles by reading roles table (case-insensitive)
        normalized = [r.lower() for r in roles if isinstance(r, str)]
        # fetch available roles from repo
        db_roles = await self.role_repo.list(limit=1000, offset=0)
        allowed = {getattr(r, "name", "").lower() for r in db_roles}
        invalid = [r for r in normalized if r not in allowed]
        if invalid:
            raise ValidationError(
                message="invalid roles",
                details=[
                    {"field": "roles", "reason": "invalid_values", "values": invalid}
                ],
            )

        selected_roles = list(filter(lambda x: x.name.lower() in normalized, db_roles))

        # enforce institution_id for institution_admin
        if "institution_admin" in normalized and not institution_id:
            raise ValidationError(
                message="institution_id is required for institution_admin role",
                details=[
                    {
                        "field": "institution_id",
                        "reason": "required_for_role",
                        "role": "institution_admin",
                    }
                ],
            )

        # delegate core user creation
        create_user_uc = CreateUser(self.user_repo, self.institution_repo)

        user = await create_user_uc.execute(
            email=email,
            password=password,
            roles=selected_roles,
            institution_id=institution_id,
        )

        # if candidate role present, create candidate profile
        if "candidate" in normalized:
            if not candidate_profile or not isinstance(candidate_profile, dict):
                raise ValidationError(
                    message="candidate_profile is required for candidate role",
                    details=[{"field": "candidate_profile", "reason": "required"}],
                )

            create_profile_uc = CreateCandidateProfile(
                self.candidate_repo, self.user_repo
            )
            cpf = candidate_profile.get("cpf")
            dob = candidate_profile.get("date_of_birth")
            full_name_cp = candidate_profile.get("full_name")
            await create_profile_uc.execute(
                user_id=user.id, full_name=full_name_cp, date_of_birth=dob, cpf=cpf
            )

        return user
