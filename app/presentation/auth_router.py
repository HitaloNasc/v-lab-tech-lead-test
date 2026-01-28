from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user_use_cases import AuthenticateUser
from app.infrastructure.db import get_db
from app.infrastructure.repositories.user_repository_sqlalchemy import (
    UserRepositorySQLAlchemy,
)
from app.infrastructure.repositories.role_repository_sqlalchemy import (
    RoleRepositorySQLAlchemy,
)
from app.infrastructure.repositories.institution_repository_sqlalchemy import (
    InstitutionRepositorySQLAlchemy,
)
from app.infrastructure.repositories.candidate_profile_repository_sqlalchemy import (
    CandidateProfileRepositorySQLAlchemy,
)
from app.presentation.schemas import (
    TokenResponse,
    UserLogin,
    RegistrationRequest,
    UserRead,
)
from app.application.registration_use_cases import RegisterUser

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


def get_institution_repo(db: AsyncSession = Depends(get_db)):
    return InstitutionRepositorySQLAlchemy(lambda: db)


def get_candidate_repo(db: AsyncSession = Depends(get_db)):
    return CandidateProfileRepositorySQLAlchemy(lambda: db)


def get_role_repo(db: AsyncSession = Depends(get_db)):
    return RoleRepositorySQLAlchemy(lambda: db)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_in: UserLogin, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)
):
    use_case = AuthenticateUser(repo)
    result = await use_case.execute(user_in.email, user_in.password)
    # result contains access_token, token_type, user
    return {
        "access_token": result["access_token"],
        "token_type": result.get("token_type", "bearer"),
    }


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    reg_in: RegistrationRequest,
    user_repo: UserRepositorySQLAlchemy = Depends(get_user_repo),
    institution_repo: InstitutionRepositorySQLAlchemy = Depends(get_institution_repo),
    candidate_repo: CandidateProfileRepositorySQLAlchemy = Depends(get_candidate_repo),
    role_repo: RoleRepositorySQLAlchemy = Depends(get_role_repo),
):
    use_case = RegisterUser(user_repo, institution_repo, candidate_repo, role_repo)
    user = await use_case.execute(
        reg_in.email,
        reg_in.password,
        reg_in.roles,
        reg_in.institution_id,
        reg_in.candidate_profile.dict() if reg_in.candidate_profile else None,
    )
    return UserRead.from_domain(user)
