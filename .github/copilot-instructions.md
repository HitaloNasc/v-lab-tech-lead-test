# Copilot Instructions

Academic offers management platform (courses, scholarships, internships) for Brazilian universities. Backend API with LGPD compliance, RBAC, and 100K+ user scalability target.

## Architecture Overview

**Four-layer architecture** (see [docs/architecture/3_adr_001_layers.md](docs/architecture/3_adr_001_layers.md)):

| Layer | Responsibility | Examples |
|-------|----------------|----------|
| **Presentation** | HTTP concerns only (routes, status codes, auth guards) | Controllers, Pydantic schemas |
| **Application** | Use cases, business orchestration, audit events | `CreateOffer`, `CreateApplication` |
| **Domain** | Entities, invariants, repository interfaces (ports) | `Offer`, `Application`, `CandidateProfile` |
| **Infrastructure** | Concrete implementations, DB, external services | PostgreSQL repos, JWT provider, bcrypt |

**Key constraint**: Domain layer must be framework-agnostic. Never import HTTP/ORM/infrastructure details into Domain.

**Framework:** The Presentation layer uses FastAPI for HTTP routing, dependency injection, and OpenAPI schema generation. Controllers should be implemented as FastAPI routers, using Pydantic for request/response schemas.

## Domain Entities & Rules

Core entities: `Institution` → `Program` → `Offer` ← `Application` ← `CandidateProfile` ← `User` (with `Role`/`UserRole` for RBAC)

**Business rules to enforce**:
- `Application` unique per `(candidate_profile_id, offer_id)` — return 409 on duplicate
- `Offer.application_deadline > Offer.publication_date` — return 422 on violation
- Candidate cannot apply to expired offers — validate deadline in use case
- Only `admin` role can create/modify offers — check RBAC in use case layer

## API Conventions

RESTful with URL versioning `/api/v1`. See [docs/architecture/10_adr_008_api_conventions.md](docs/architecture/10_adr_008_api_conventions.md).

```
# Pagination: limit/offset (default limit=20, max=100)
GET /api/v1/offers?limit=20&offset=0&institution_id=...&type=course&status=published

# Error envelope (always this structure)
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...], "request_id": "..." } }
```

**Status codes**: 201 Created, 409 Conflict (duplicate application), 422 Unprocessable (semantic validation), 403 Forbidden (RBAC)

## Data & LGPD

- **Soft delete** for all domain entities (`deleted_at`, `deleted_by`, `deletion_reason`)
- **Audit tables** are append-only: `AuditEvent` (mutations), `DataAccessLog` (reads of personal data)
- **Never log PII** (emails, CPF, passwords) — use `request_id` for correlation
- Filter queries with `deleted_at IS NULL` by default

## Observability

Structured JSON logs with fields: `timestamp`, `level`, `service`, `env`, `request_id`, `message`. Propagate `X-Request-Id` header.

Health endpoints: `GET /health` (liveness), `GET /ready` (readiness with DB check)

## Tech Stack Decisions


- **FastAPI** for API layer (routing, DI, OpenAPI docs)

## Code Patterns

```python
# Use case in Application layer — orchestrates domain + repos
class CreateApplication:
    def execute(self, candidate_id: UUID, offer_id: UUID) -> Application:
        # 1. Validate offer exists and not expired
        # 2. Check uniqueness (candidate, offer)
        # 3. Create Application entity
        # 4. Persist via repository interface
        # 5. Emit AuditEvent
```

When adding features: create use case in Application layer → define/extend domain entities → implement repository in Infrastructure.
