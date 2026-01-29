from typing import Optional
from uuid import UUID

from app.domain.errors import NotFoundError, ValidationError, ForbiddenError
from app.domain.institution_repository import InstitutionRepository
from app.domain.role import Role
from app.domain.user import User
from app.domain.user_repository import UserRepository
from app.domain.candidate_profile_repository import CandidateProfileRepository
from app.infrastructure.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class CreateUser:
    def __init__(self, repo: UserRepository, institution_repo: InstitutionRepository):
        self.repo = repo
        self.institution_repo = institution_repo

    async def execute(
        self,
        email: str,
        password: str,
        roles: Optional[list[Role]] = None,
        institution_id: Optional[UUID] = None,
    ) -> User:
        # validate password strength before hashing
        pw_issues = self._password_issues(password)
        if pw_issues:
            raise ValidationError(
                message="weak password",
                details=pw_issues,
            )

        # hash password
        hashed = hash_password(password)

        # validation rules: admin requires institution_id; candidate must have no institution
        role_names = (
            [getattr(r, "name", str(r)).lower() for r in roles] if roles else []
        )
        if "institution_admin" in role_names and not institution_id:
            raise ValidationError(
                message="admin users must have institution_id",
                details=[
                    {"field": "institution_id", "reason": "required for admin role"}
                ],
            )
        if "candidate" in role_names and institution_id is not None:
            raise ValidationError(
                message="candidate users cannot be linked to an institution",
                details=[
                    {
                        "field": "institution_id",
                        "reason": "must be null for candidate role",
                    }
                ],
            )

        # validate institution exists when provided
        if institution_id:
            inst = await self.institution_repo.get_by_id(institution_id)
            if not inst:
                raise NotFoundError(
                    message="Institution not found",
                    details=[{"field": "institution_id", "reason": "not found"}],
                )

        user = User(
            email=email,
            hashed_password=hashed,
            roles=roles,
            institution_id=institution_id,
        )
        return await self.repo.create(user)

    def _password_issues(self, pw: str) -> list:
        issues = []
        if not pw or len(pw) < 8:
            issues.append({"field": "password", "reason": "too_short"})
        if not any(c.islower() for c in pw):
            issues.append({"field": "password", "reason": "no_lowercase"})
        if not any(c.isupper() for c in pw):
            issues.append({"field": "password", "reason": "no_uppercase"})
        if not any(c.isdigit() for c in pw):
            issues.append({"field": "password", "reason": "no_digit"})
        special = set("!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~")
        if not any(c in special for c in pw):
            issues.append({"field": "password", "reason": "no_special_char"})
        return issues


class AuthenticateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError(
                message="User not found",
                details=[{"field": "email", "reason": "not found"}],
            )
        if not verify_password(password, user.hashed_password):
            raise ValidationError(
                message="Invalid credentials",
                details=[{"field": "password", "reason": "invalid"}],
            )

        # include roles as array claim for downstream consumers
        roles_claim = []
        if hasattr(user, "roles") and user.roles:
            for r in user.roles:
                try:
                    roles_claim.append(r.name)
                except Exception:
                    continue
        token = create_access_token(str(user.id), extra_claims={"roles": roles_claim})
        return {"access_token": token, "token_type": "bearer", "user": user}


class GetUserById:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, user_id: UUID) -> Optional[User]:
        return await self.repo.get_by_id(user_id)


class UpdateUser:
    def __init__(
        self,
        repo: UserRepository,
        institution_repo: InstitutionRepository,
        profile_repo: CandidateProfileRepository = None,
    ):
        self.repo = repo
        self.institution_repo = institution_repo
        self.profile_repo = profile_repo

    async def execute(
        self,
        user_id: UUID,
        updates: dict,
        requester_id: UUID,
        requester_roles: Optional[list] = None,
    ) -> User:
        current = await self.repo.get_by_id(user_id)
        if not current:
            raise NotFoundError(
                message="User not found",
                details=[{"field": "id", "reason": "not found"}],
            )

        normalized_requester_roles = [str(r).lower() for r in (requester_roles or [])]
        is_sys_admin = "sys_admin" in normalized_requester_roles
        is_institution_admin = "institution_admin" in normalized_requester_roles
        is_candidate = "candidate" in normalized_requester_roles

        # authorization: sys_admin can update any user; others only own
        if not is_sys_admin and str(requester_id) != str(user_id):
            raise ForbiddenError(
                message="Not allowed to update other users",
                details=[{"field": "user_id", "reason": "forbidden"}],
            )

        # prevent institution_admin from changing institution_id
        if is_institution_admin and "institution_id" in updates:
            raise ForbiddenError(
                message="institution_admin cannot change institution_id",
                details=[{"field": "institution_id", "reason": "forbidden"}],
            )

        # determine effective roles after update
        new_roles = None
        if "roles" in updates and updates["roles"] is not None:
            new_roles = [
                r if hasattr(r, "name") else Role(name=r) for r in updates["roles"]
            ]
        else:
            new_roles = current.roles

        role_names = (
            [getattr(r, "name", str(r)).lower() for r in new_roles] if new_roles else []
        )

        inst_id = updates.get(
            "institution_id", getattr(current, "institution_id", None)
        )

        if "institution_admin" in role_names and not inst_id:
            raise ValidationError(
                message="admin users must have institution_id",
                details=[
                    {"field": "institution_id", "reason": "required for admin role"}
                ],
            )
        if "candidate" in role_names and inst_id is not None:
            raise ValidationError(
                message="candidate users cannot be linked to an institution",
                details=[
                    {
                        "field": "institution_id",
                        "reason": "must be null for candidate role",
                    }
                ],
            )

        # validate institution exists when provided
        if inst_id:
            inst = await self.institution_repo.get_by_id(inst_id)
            if not inst:
                raise NotFoundError(
                    message="Institution not found",
                    details=[{"field": "institution_id", "reason": "not found"}],
                )

        # apply updates
        # handle password hashing
        if "password" in updates and updates["password"]:
            current.hashed_password = hash_password(updates["password"])

        if "roles" in updates and updates["roles"] is not None:
            current.roles = updates["roles"]

        # handle candidate_profile updates
        if "candidate_profile" in updates:
            if not is_candidate:
                raise ForbiddenError(
                    message="Only candidate can update candidate_profile",
                    details=[{"field": "candidate_profile", "reason": "forbidden"}],
                )
            if not self.profile_repo:
                raise ValidationError(
                    message="candidate_profile repository not configured",
                )
            profile = await self.profile_repo.get_by_user_id(user_id)
            if not profile:
                raise NotFoundError(
                    message="CandidateProfile not found",
                    details=[{"field": "user_id", "reason": "not found"}],
                )
            for p_field, p_value in updates["candidate_profile"].items():
                setattr(profile, p_field, p_value)
            await self.profile_repo.update(profile)

        # apply remaining top-level fields
        skip_fields = {"password", "roles", "candidate_profile"}
        for field, value in updates.items():
            if field in skip_fields:
                continue
            setattr(current, field, value)

        return await self.repo.update(current)


class DeleteUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(
        self, user_id: UUID, deleted_by: UUID, reason: Optional[str] = None
    ):
        return await self.repo.soft_delete(user_id, deleted_by, reason)
