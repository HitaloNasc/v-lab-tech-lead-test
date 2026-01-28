from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Date,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from app.domain.institution import Institution
from app.domain.offer import Offer, OfferStatus, OfferType
from app.domain.program import Program
from app.domain.user import User
from app.domain.role import Role
from app.domain.application import Application

Base = declarative_base()


class OfferModel(Base):
    __tablename__ = "offers"
    __table_args__ = (
        CheckConstraint(
            "application_deadline > publication_date",
            name="ck_offer_deadline_after_publication",
        ),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    institution_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    program_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("programs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SqlEnum(OfferType), nullable=False, index=True)
    status = Column(SqlEnum(OfferStatus), nullable=False, index=True)
    publication_date = Column(DateTime(timezone=True), nullable=False)
    application_deadline = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    # Note: roles are associated to users via the `user_roles` association table.
    # Offers do not have a direct many-to-many to roles; the relationship
    # belonged on UserModel. Removed incorrect mapping here to avoid
    # NoForeignKeysError.

    def to_domain(self) -> Offer:
        return Offer(
            id=self.id,
            institution_id=self.institution_id,
            program_id=self.program_id,
            title=self.title,
            description=self.description,
            type=self.type,
            status=self.status,
            publication_date=self.publication_date,
            application_deadline=self.application_deadline,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, offer: Offer) -> "OfferModel":
        return cls(
            id=offer.id,
            institution_id=offer.institution_id,
            program_id=getattr(offer, "program_id", None),
            title=offer.title,
            description=offer.description,
            type=offer.type,
            status=offer.status,
            publication_date=offer.publication_date,
            application_deadline=offer.application_deadline,
            created_at=offer.created_at,
            updated_at=offer.updated_at,
            deleted_at=offer.deleted_at,
            deleted_by=offer.deleted_by,
            deletion_reason=offer.deletion_reason,
        )

    def update_from_domain(self, offer: Offer):
        self.title = offer.title
        self.description = offer.description
        # allow updating program_id when present
        if hasattr(offer, "program_id"):
            self.program_id = offer.program_id
        self.type = offer.type
        self.status = offer.status
        self.publication_date = offer.publication_date
        self.application_deadline = offer.application_deadline
        self.updated_at = datetime.utcnow()
        # Não atualiza deleted_at, deleted_by, deletion_reason aqui

    # relationships
    program = relationship("ProgramModel", backref="offers")
    institution = relationship("InstitutionModel")


class InstitutionModel(Base):
    __tablename__ = "institutions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    def to_domain(self) -> "Institution":
        return Institution(
            id=self.id,
            name=self.name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, institution: "Institution") -> "InstitutionModel":
        return cls(
            id=institution.id,
            name=institution.name,
            description=institution.description,
            created_at=institution.created_at,
            updated_at=institution.updated_at,
            deleted_at=institution.deleted_at,
            deleted_by=institution.deleted_by,
            deletion_reason=institution.deletion_reason,
        )

    def update_from_domain(self, institution: "Institution"):
        self.name = institution.name
        self.description = institution.description
        self.updated_at = datetime.utcnow()


class ProgramModel(Base):
    __tablename__ = "programs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    institution_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    def to_domain(self) -> Program:
        return Program(
            id=self.id,
            institution_id=self.institution_id,
            name=self.name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    # relationship to InstitutionModel (optional convenience)
    institution = relationship("InstitutionModel", backref="programs")

    @classmethod
    def from_domain(cls, program: Program) -> "ProgramModel":
        return cls(
            id=program.id,
            institution_id=program.institution_id,
            name=program.name,
            description=program.description,
            created_at=program.created_at,
            updated_at=program.updated_at,
            deleted_at=program.deleted_at,
            deleted_by=program.deleted_by,
            deletion_reason=program.deletion_reason,
        )

    def update_from_domain(self, program: Program):
        self.name = program.name
        self.description = program.description
        self.updated_at = datetime.utcnow()


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def to_domain(self) -> Role:
        return Role(
            id=self.id,
            name=self.name,
            description=self.description,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, role: Role) -> "RoleModel":
        return cls(
            id=role.id,
            name=role.name,
            description=getattr(role, "description", None),
            created_at=(
                role.created_at
                if (
                    hasattr(role, "created_at")
                    and getattr(role, "created_at") is not None
                )
                else datetime.utcnow()
            ),
        )

    def update_from_domain(self, role: Role):
        self.name = role.name
        self.description = getattr(role, "description", self.description)
        self.updated_at = datetime.utcnow()

    # association object side: collection of UserRoleModel
    user_roles = relationship(
        "UserRoleModel",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # convenience proxy to access users via association object
    users = association_proxy("user_roles", "user")


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # relationships (explicit association object)
    user = relationship("UserModel", back_populates="user_roles")
    role = relationship("RoleModel", back_populates="user_roles")


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    institution_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # role column removed — roles are modeled via many-to-many `user_roles` association
    # association relationship defined below
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    def to_domain(self) -> "User":
        # map role string to Role enum if possible
        # build roles list from related RoleModel objects if loaded
        roles = []
        if hasattr(self, "roles") and self.roles is not None:
            for r in self.roles:
                try:
                    roles.append(Role(id=r.id, name=r.name, created_at=r.created_at))
                except Exception:
                    continue

        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            roles=roles,
            institution_id=getattr(self, "institution_id", None),
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, user: "User") -> "UserModel":
        return cls(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            institution_id=getattr(user, "institution_id", None),
            # roles are handled via association table; do not write here
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            deleted_by=user.deleted_by,
            deletion_reason=user.deletion_reason,
        )

    def update_from_domain(self, user: "User"):
        self.email = user.email
        if hasattr(user, "institution_id"):
            self.institution_id = user.institution_id
        if hasattr(user, "hashed_password") and user.hashed_password:
            self.hashed_password = user.hashed_password
        # roles are managed via the `user_roles` association and repository logic
        self.updated_at = datetime.utcnow()

    # optional convenience relationship to InstitutionModel
    # explicit association object from User -> UserRoleModel
    user_roles = relationship(
        "UserRoleModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # convenience proxy to access RoleModel objects via the association
    roles = association_proxy("user_roles", "role")

    # optional convenience relationship to InstitutionModel
    institution = relationship("InstitutionModel")


class CandidateProfileModel(Base):
    __tablename__ = "candidate_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    cpf = Column(String(64), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    # relationship to user (optional convenience)
    user = relationship("UserModel")

    def to_domain(self) -> "CandidateProfile":
        from app.domain.candidate_profile import CandidateProfile

        return CandidateProfile(
            id=self.id,
            user_id=self.user_id,
            full_name=self.full_name,
            date_of_birth=self.date_of_birth,
            cpf=self.cpf,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, profile: "CandidateProfile") -> "CandidateProfileModel":
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            full_name=profile.full_name,
            date_of_birth=profile.date_of_birth,
            cpf=profile.cpf,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            deleted_at=profile.deleted_at,
            deleted_by=profile.deleted_by,
            deletion_reason=profile.deletion_reason,
        )

    def update_from_domain(self, profile: "CandidateProfile"):
        self.full_name = profile.full_name
        self.date_of_birth = profile.date_of_birth
        self.cpf = profile.cpf
        self.updated_at = datetime.utcnow()


class ApplicationModel(Base):
    __tablename__ = "applications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    candidate_profile_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    offer_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("offers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status = Column(String(50), nullable=False, default="submitted", index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deletion_reason = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id", "offer_id", name="uq_applications_candidate_offer"
        ),
    )

    def to_domain(self) -> Application:
        return Application(
            id=self.id,
            candidate_profile_id=self.candidate_profile_id,
            offer_id=self.offer_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            deleted_by=self.deleted_by,
            deletion_reason=self.deletion_reason,
        )

    @classmethod
    def from_domain(cls, application: Application) -> "ApplicationModel":
        return cls(
            id=application.id,
            candidate_profile_id=application.candidate_profile_id,
            offer_id=application.offer_id,
            status=getattr(application, "status", "submitted"),
            created_at=application.created_at,
            updated_at=application.updated_at,
            deleted_at=application.deleted_at,
            deleted_by=application.deleted_by,
            deletion_reason=application.deletion_reason,
        )

    def update_from_domain(self, application: Application):
        self.status = application.status
        self.updated_at = datetime.utcnow()
