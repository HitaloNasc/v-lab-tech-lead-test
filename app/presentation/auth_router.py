from fastapi import APIRouter, Depends, status
from app.infrastructure.repositories.user_repository_sqlalchemy import UserRepositorySQLAlchemy
from app.application.user_use_cases import AuthenticateUser
from app.presentation.schemas import UserLogin, TokenResponse
from app.infrastructure.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepositorySQLAlchemy(lambda: db)


@router.post("/token", response_model=TokenResponse)
async def login(user_in: UserLogin, repo: UserRepositorySQLAlchemy = Depends(get_user_repo)):
    use_case = AuthenticateUser(repo)
    result = await use_case.execute(user_in.email, user_in.password)
    # result contains access_token, token_type, user
    return {"access_token": result["access_token"], "token_type": result.get("token_type", "bearer")}
