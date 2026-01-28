from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt

from app.config.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None, extra_claims: dict = None
) -> str:
    to_encode = {"sub": subject}
    if extra_claims:
        to_encode.update(extra_claims)
    expire = datetime.utcnow() + (
        expires_delta or timedelta(seconds=settings.JWT_EXPIRES_IN)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
