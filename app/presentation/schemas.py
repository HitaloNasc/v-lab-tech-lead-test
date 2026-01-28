from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.domain.offer import OfferType, OfferStatus, Offer
from app.domain.role import Role as RoleDomain


class OfferCreate(BaseModel):
    institution_id: UUID
    program_id: Optional[UUID]
    title: str
    description: Optional[str]
    type: OfferType
    publication_date: datetime
    application_deadline: datetime


class OfferUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    type: Optional[OfferType]
    status: Optional[OfferStatus]
    publication_date: Optional[datetime]
    application_deadline: Optional[datetime]
    program_id: Optional[UUID]


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


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str]
    roles: Optional[List[str]]


class UserUpdate(BaseModel):
    full_name: Optional[str]
    password: Optional[str]
    roles: Optional[List[str]]
    is_active: Optional[bool]


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    roles: List[dict]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user):
        data = user.__dict__.copy()
        # never expose hashed_password
        data.pop("hashed_password", None)
        # convert role domain objects to serializable dicts
        roles = []
        if hasattr(user, "roles") and user.roles:
            for r in user.roles:
                try:
                    roles.append({"id": r.id, "name": r.name})
                except Exception:
                    continue
        data["roles"] = roles
        return cls(**data)


class RoleCreate(BaseModel):
    name: str
    description: Optional[str]


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

    @classmethod
    def from_domain(cls, role: RoleDomain):
        return cls(id=role.id, name=role.name, description=getattr(role, "description", None), created_at=getattr(role, "created_at", datetime.utcnow()))


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
                        {"field": "application_deadline", "reason": "must be after publication_date"}
                    ],
                    "request_id": "req_e353920d7e7c4557",
                }
            }
        }


class InstitutionCreate(BaseModel):
    name: str
    description: Optional[str]


class InstitutionUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


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
    name: str
    description: Optional[str]


class ProgramUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


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


class CandidateProfileCreate(BaseModel):
    user_id: UUID
    full_name: str
    date_of_birth: Optional[str]
    cpf: Optional[str]


class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str]
    date_of_birth: Optional[str]
    cpf: Optional[str]


class CandidateProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    date_of_birth: Optional[str]
    cpf: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    deletion_reason: Optional[str]

    @classmethod
    def from_domain(cls, profile):
        return cls(**profile.__dict__)


class ApplicationCreate(BaseModel):
    candidate_profile_id: UUID
    offer_id: UUID


class ApplicationUpdate(BaseModel):
    status: Optional[str]


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
