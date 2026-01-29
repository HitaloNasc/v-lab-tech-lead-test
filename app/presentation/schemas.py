from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, constr

from app.domain.offer import Offer, OfferStatus, OfferType
from app.domain.role import Role as RoleDomain

# -----------------------------
# Offers
# -----------------------------


class OfferCreate(BaseModel):
    institution_id: UUID
    program_id: Optional[UUID] = None
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    type: OfferType
    publication_date: date
    application_deadline: date


class OfferUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    type: Optional[OfferType] = None
    status: Optional[OfferStatus] = None
    publication_date: Optional[date] = None
    application_deadline: Optional[date] = None
    program_id: Optional[UUID] = None


class OfferRead(BaseModel):
    id: UUID
    institution_id: UUID
    program_id: Optional[UUID]
    title: str
    description: Optional[str]
    type: OfferType
    status: OfferStatus
    publication_date: datetime
    application_deadline: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, offer: Offer):
        return cls(**offer.__dict__)


# -----------------------------
# Users & Roles
# -----------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # never store raw password
    roles: Optional[List[str]] = None
    institution_id: Optional[UUID] = (
        None  # required when role includes 'admin' (business rule)
    )


class UserUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=8, max_length=256)
    roles: Optional[List[str]] = None
    institution_id: Optional[UUID] = (
        None  # required when role includes 'admin' (business rule)
    )
    candidate_profile: Optional["CandidateProfileUpdate"] = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    roles: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None
    deletion_reason: Optional[str] = None
    institution_id: Optional[UUID]

    @classmethod
    def from_domain(cls, user):
        data = user.__dict__.copy()
        # LGPD/Security: never expose hashed_password
        data.pop("hashed_password", None)

        roles: List[Dict[str, Any]] = []
        if getattr(user, "roles", None):
            for r in user.roles:
                try:
                    roles.append(
                        {
                            "id": r.id,
                            "name": r.name,
                            "description": getattr(r, "description", None),
                        }
                    )
                except Exception:
                    continue

        data["roles"] = roles
        return cls(**data)


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=300)


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, role: RoleDomain):
        return cls(
            id=role.id,
            name=role.name,
            description=getattr(role, "description", None),
            created_at=getattr(role, "created_at", datetime.utcnow()),
            updated_at=getattr(role, "updated_at", None),
            deleted_at=getattr(role, "deleted_at", None),
        )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# Error envelope
# -----------------------------


class ErrorDetail(BaseModel):
    field: Optional[str]
    reason: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]]
    request_id: Optional[str]


class ErrorEnvelope(BaseModel):
    error: ErrorBody

    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "application_deadline must be after publication_date",
                    "details": [
                        {
                            "field": "application_deadline",
                            "reason": "must be after publication_date",
                        }
                    ],
                    "request_id": "req_e353920d7e7c4557",
                }
            }
        }


# -----------------------------
# Institutions & Programs
# -----------------------------


class InstitutionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class InstitutionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class InstitutionRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, institution):
        return cls(**institution.__dict__)


class ProgramCreate(BaseModel):
    institution_id: UUID
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProgramUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProgramRead(BaseModel):
    id: UUID
    institution_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, program):
        return cls(**program.__dict__)


# -----------------------------
# Candidate profile (PII)
# -----------------------------
# LGPD note:
# CandidateProfile contains personal data. Only expose it when authorized
# (self or admin of same institution with active consent). This policy is enforced
# in Application Layer; schemas just ensure we don't accidentally leak credentials.


class CandidateProfileCreate(BaseModel):
    user_id: UUID
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: Optional[date] = None
    cpf: Optional[str] = Field(
        default=None, max_length=14
    )  # do not validate format here unless required


class CandidateProfileForRegistration(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: Optional[date] = None
    cpf: Optional[
        constr(max_length=14, pattern=r"^\d{3}\.??\d{3}\.??\d{3}-?\d{2}$")
    ] = None


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    roles: List[str]
    institution_id: Optional[UUID] = None
    candidate_profile: Optional[CandidateProfileForRegistration] = None


class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    date_of_birth: Optional[date] = None
    cpf: Optional[str] = Field(default=None, max_length=14)


class CandidateProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    date_of_birth: Optional[date]
    cpf: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, profile):
        return cls(**profile.__dict__)


# -----------------------------
# Applications
# -----------------------------


class ApplicationCreate(BaseModel):
    candidate_profile_id: UUID
    offer_id: UUID


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None


class ApplicationRead(BaseModel):
    id: UUID
    candidate_profile_id: UUID
    offer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, app):
        return cls(**app.__dict__)


# resolve forward refs
UserUpdate.update_forward_refs()
