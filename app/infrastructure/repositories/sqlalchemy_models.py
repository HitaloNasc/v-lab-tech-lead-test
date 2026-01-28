from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.domain.institution import Institution
from app.domain.offer import Offer, OfferStatus, OfferType
from app.domain.program import Program
from app.domain.user import User
from app.domain.role import Role

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

    # many-to-many relationship to roles via association table
    roles = relationship("RoleModel", secondary="user_roles", backref="users")

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
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def to_domain(self) -> Role:
        return Role(id=self.id, name=self.name, description=self.description, created_at=self.created_at)

    @classmethod
    def from_domain(cls, role: Role) -> "RoleModel":
        return cls(
            id=role.id,
            name=role.name,
            description=getattr(role, "description", None),
            created_at=role.created_at if hasattr(role, "created_at") else None,
        )

    def update_from_domain(self, role: Role):
        self.name = role.name
        self.description = getattr(role, "description", self.description)
        self.updated_at = datetime.utcnow()


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # relationships (optional convenience)
    role = relationship("RoleModel")
    # user relationship is optional here to avoid circular import issues



class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    # role column removed — roles are modeled via many-to-many `user_roles` association
    # association relationship defined below
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
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
            full_name=self.full_name,
            roles=roles,
            is_active=self.is_active,
            last_login=self.last_login,
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
            full_name=user.full_name,
            # roles are handled via association table; do not write here
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            deleted_by=user.deleted_by,
            deletion_reason=user.deletion_reason,
        )

    def update_from_domain(self, user: "User"):
        self.email = user.email
        if hasattr(user, "hashed_password") and user.hashed_password:
            self.hashed_password = user.hashed_password
        self.full_name = user.full_name
        # roles are managed via the `user_roles` association and repository logic
        self.is_active = user.is_active
        self.updated_at = datetime.utcnow()
