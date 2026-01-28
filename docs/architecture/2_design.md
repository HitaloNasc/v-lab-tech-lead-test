# Design Arquitetural — Plataforma de Gestão de Ofertas e Candidaturas (V-LAB)

**Data:** 26/01/2026  
**Autor:** Hítalo Nascimento  
**Status:** Rascunho (atualizado com regras de acesso/consentimento e vínculo institucional de admins)  

**Referências:**
- [Captura de Requisitos](./1_requirements_capture.md)
- [Modelo Conceitual de Dados (PlantUML)](./diagrams/concept-data-model.puml)

---

## 1. Visão Geral

### 1.1 Contexto
Plataforma para universidades brasileiras gerenciarem **ofertas acadêmicas** (cursos, bolsas, estágios) e **candidaturas**, com consumo por múltiplos clientes (web/mobile/integrações). O sistema deve operar com **dados sensíveis**, exigindo conformidade com LGPD, além de escalar para **100K+ usuários simultâneos**, mantendo manutenibilidade (time backend pequeno).

### 1.2 Objetivo
Fornecer uma API versionada (v1) que suporte:
- Autenticação e autorização (RBAC + regras contextuais)
- CRUD de ofertas com paginação e filtros
- Criação e gerenciamento de candidaturas com regras de negócio
- **Controle de acesso a dados pessoais baseado em instituição + consentimento**
- Rastreabilidade (auditoria de alterações e acessos) para LGPD

### 1.3 Escopo do núcleo funcional
Inclui:
- User registration + login + JWT
- CRUD Offers
- Applications (criar, listar por usuário, atualizar status)
- Regras: unicidade de candidatura por oferta e validação de prazo
- RBAC: apenas admin cria oferta
- **Admin institucional:** usuários `admin` possuem vínculo com `Institution` via `User.institution_id`
- **LGPD logging (recomendado no design):** auditoria de alteração + acesso

---

## 2. Modelo Conceitual de Dados

### 2.1 Entidades principais (conceitual)

- **[Institution]**: Instituição/universidade proprietária das ofertas e programas. Centraliza o “dono” institucional do catálogo e atua como chave de particionamento lógico (multi-instituição).

- **[Program]**: Programas vinculados a uma `institution` (ex.: programa de pós, edital, trilha), permitindo organizar ofertas por contexto institucional.

- **[Offer]**: Oferta acadêmica publicada por uma `institution` e opcionalmente associada a um `program`. Contém tipo, status e janelas de publicação/candidatura (`application_deadline > publication_date`).

- **[User]**: Identidade autenticável (cadastro/login) com credenciais (hash de senha) e trilha de ciclo de vida (soft delete + motivo).  
  **Atualização importante:** `User` possui `institution_id` **opcional**, usado para representar **admins institucionais**. Usuários candidatos não possuem vínculo institucional.

- **[Role]**: Catálogo de perfis de acesso (`admin`, `candidate`) usado para autorização (RBAC).

- **[UserRole]**: Junção N:N entre `user` e `role`, permitindo múltiplos papéis por usuário.

- **[CandidateProfile]**: Perfil do candidato com dados pessoais separados de `User` (privacy-by-design), 1:1 com `User`. Não armazena consentimento por candidatura; consentimento contextual reside em `Consent`.

- **[Application]**: Candidatura de um candidato (`candidate_profile`) para uma `offer`. Impõe unicidade (`candidate_profile_id`, `offer_id`) e valida prazo (não aplicar após `application_deadline`).

- **[Consent]**: Registro de consentimento **contextual e versionado** associado a `application` e ao titular (`user`). Suporta revogação (`revoked_at`) e evidências técnicas (IP, user agent, hash).

#### LGPD / Audit (opcional na implementação inicial, recomendado no design)

- **[AuditEvent]**: Auditoria append-only de alterações (quem, quando, o quê, antes/depois), com contexto técnico.
- **[DataAccessLog]**: Log de acesso/leitura a dados pessoais, principalmente quando `actor != titular`.

---

### 2.2 Regras e constraints no modelo de dados

As regras e constraints a seguir derivam diretamente dos requisitos funcionais (RFs) e garantem consistência, integridade e conformidade legal (LGPD) no modelo de dados.

- **Unicidade de candidatura (RF-009):**  
  `Application` deve ser única por par (`candidate_profile_id`, `offer_id`).  
  *Implementação sugerida:* `UNIQUE (candidate_profile_id, offer_id)`.

- **Integridade temporal da oferta (RF-010):**  
  `Offer` respeita `application_deadline > publication_date`.  
  *Implementação sugerida:* `CHECK` no banco ou validação obrigatória no caso de uso de criação/atualização.

- **Validação de prazo de candidatura (RF-011):**  
  Não permitir criar `Application` se `application_deadline` expirou ou a `Offer` está `closed`.  
  *Implementação sugerida:* validação em `CreateApplication`.

- **Controle de acesso por papel (RBAC) (RF-005):**  
  Apenas `admin` pode criar/atualizar/deletar `Offer`.  
  *Implementação sugerida:* guard/middleware + validação no caso de uso.

- **Admin institucional (User.institution_id):**  
  - Se `User` possuir role `admin`, então `institution_id` deve estar preenchido.  
  - Se `User` possuir role `candidate`, então `institution_id` deve ser nulo.  
  *Implementação sugerida:* validação no fluxo de criação/gestão de usuários (Application Layer) e/ou constraint lógica na aplicação.

- **Separação de identidade e dados pessoais (privacy-by-design):**  
  Dados pessoais do candidato residem em `CandidateProfile`, mantendo `User` focado em authn/authz.

- **Autorização contextual para leitura de CandidateProfile (RF-014, RF-015):**  
  `CandidateProfile` só pode ser lido:
  - pelo próprio titular; ou
  - por admin institucional **da mesma instituição da Offer** (`User.institution_id == Offer.institution_id`) **e** com **Consent ativo** no contexto de uma `Application` relacionada.  
  *Implementação sugerida:* política de autorização (ABAC) no caso de uso/serviço, gerando `DataAccessLog` quando actor != titular.

- **Consentimento contextual e versionado (RF-015):**  
  `Consent` deve ser contextual à candidatura (`application_id`) e versionado (`terms_version`, `scope`).  
  *Recomendação:* `UNIQUE (application_id, scope, terms_version)`.

- **Soft delete e retenção histórica (LGPD):**  
  `User`, `CandidateProfile`, `Offer`, `Application` usam soft delete (`deleted_at`) para preservar histórico e integridade referencial.

- **Auditoria de alterações e acessos (RF-013):**  
  - Mudanças relevantes geram `AuditEvent` (append-only).  
  - Leituras de dados pessoais por admins geram `DataAccessLog`.

---

## 3. Arquitetura de Camadas

### 3.1 Motivação
A separação em camadas reduz acoplamento, facilita testes, suporta mudanças frequentes de requisitos e melhora a manutenibilidade para um time pequeno.

### 3.2 Visão em camadas (alto nível)
![alt text](./diagrams/layers_simple.png)

### 3.3 Responsabilidades por camada

#### Presentation Layer (API)
Responsável por:
- Rotas e contratos HTTP (v1)
- Autenticação por JWT (guard/decorator)
- Validação de input via schemas (Pydantic)
- Mapeamento de erros para HTTP status + payload padronizado
- Paginação e filtros de listagem
- CORS e rate limiting (por IP)

**Não deve conter regra de negócio** (apenas orquestração e validação de entrada/saída).

#### Application Layer (Use Cases)
Responsável por:
- Orquestrar regras de negócio entre entidades e repositórios
- Aplicar validações que dependem de estado e persistência (deadline, unicidade, status)
- **Aplicar políticas de autorização (RBAC + contexto institucional + consentimento)**
- Emitir eventos de auditoria (`AuditEvent`) e logs de acesso (`DataAccessLog`) quando aplicável
- Controlar transações quando necessário

Exemplos de casos de uso:
- `RegisterUser`
- `LoginUser`
- `CreateOffer` (admin-only)
- `ListOffers` (paginação/filtros)
- `CreateApplication` (unicidade + deadline + geração de consentimento)
- `UpdateApplicationStatus` (admin institucional)
- `GetCandidateProfile` (self ou admin institucional com consentimento) *(opcional como endpoint, mas regra deve existir)*

#### Domain Layer (Domínio)
Responsável por:
- Entidades e invariantes (Offer, Application, CandidateProfile, Consent)
- Enums e Value Objects
- Regras puras (ex.: datas válidas para Offer)
- Domínio não depende de HTTP nem de banco

#### Infrastructure Layer (Infra)
Responsável por:
- Persistência (PostgreSQL via ORM)
- Implementação de repositórios
- Integrações técnicas (hash de senha, JWT provider)
- Migrações (Alembic)
- Observabilidade (logging estruturado)

---

## 4. Contratos de API (v1)

### 4.1 Autenticação e segurança
- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- Autorização via roles (UserRole)
- Endpoints protegidos com `@require_auth`
- Rate limiting simples: `max X req/min` por IP (configurável)

> **Nota de modelagem:** usuários `admin` (institucionais) devem possuir `institution_id`.

### 4.2 Offers
- POST `/api/v1/offers` (admin-only)
- GET `/api/v1/offers?limit=20&offset=0`
- GET `/api/v1/offers/{id}`
- PUT `/api/v1/offers/{id}` (admin-only, mesma institution)
- DELETE `/api/v1/offers/{id}` (admin-only, mesma institution)
- Filtros: `institution`, `type`, `status`

**Regra adicional (consistência multi-instituição):**
- Admin só pode criar/alterar offers cuja `institution_id == user.institution_id`.

### 4.3 Applications
- POST `/api/v1/applications`
- GET `/api/v1/users/{id}/applications` (self-only)
- POST `/api/v1/applications/{id}/status` (admin-only, mesma institution da offer)

Validações obrigatórias no caso de uso:
- Unicidade por (`candidate_profile_id`, `offer_id`)
- Deadline válido (não aplicar para oferta expirada)
- Impedir aplicar em offer `closed`
- Alteração de status somente por admin institucional da offer

> **Consentimento:** ao criar candidatura, deve existir registro de `Consent` (por escopo/versão) para o contexto da candidatura.

---

## 5. Observabilidade e LGPD Logging

### 5.1 Objetivo
Garantir rastreabilidade para:
- Alterações em dados e estados críticos (auditoria)
- Acesso/leitura de dados pessoais (accountability LGPD)
- Diagnóstico de incidentes (correlação por request)

### 5.2 AuditEvent (mudança)
Registrar eventos append-only para ações como:
- `OFFER_CREATED`, `OFFER_UPDATED`, `OFFER_DELETED`
- `APPLICATION_CREATED`, `APPLICATION_STATUS_CHANGED`
- `CONSENT_REVOKED`
- `CANDIDATE_PROFILE_UPDATED`
- `USER_SOFT_DELETED`

Campos principais:
- `occurred_at`, `actor_user_id`, `action`, `entity_type`, `entity_id`, `before`, `after`, `request_id`

Boas práticas:
- Minimização: registrar apenas campos relevantes
- Evitar armazenar dados pessoais completos em `before/after` quando não necessário

### 5.3 DataAccessLog (leitura)
Registrar acessos a recursos com dados pessoais, especialmente quando:
- ator (admin) acessa dados de outro titular (candidato)
- endpoint expõe CandidateProfile/Applications ou informações correlatas

Campos principais:
- `accessed_at`, `actor_user_id`, `data_subject_user_id`, `resource`, `purpose`, `request_id`

**Regra operacional:**
- Sempre que `actor_user_id != data_subject_user_id`, gerar `DataAccessLog`.

---

## 6. Decisões Técnicas Fundamentais

### 6.1 API: REST (versionada)
- REST atende operações CRUD, fluxos de candidatura e integrações futuras.
- Versionamento via URL (`/api/v1/...`) reduz breaking changes.
- Uso consistente de verbos HTTP e códigos de status.

### 6.2 Autenticação e Autorização: JWT + RBAC (+ ABAC)
- Auth stateless via JWT.
- RBAC para operações sensíveis (ex.: admin cria offer).
- **ABAC/Contextual:** regras adicionais baseadas em:
  - vínculo institucional (`User.institution_id`)
  - ownership da `Offer` (`Offer.institution_id`)
  - existência de `Consent` ativo para acesso administrativo a dados pessoais

### 6.3 Banco de Dados: PostgreSQL
- ACID + constraints (UNIQUE, CHECK, FK).
- Tipos: UUID, timestamptz, citext, jsonb, inet.
- Bom para paginação/índices e multi-instituição.
- Adequado para soft delete e auditoria.

### 6.4 Stack Tecnológica
- Python 3.x
- FastAPI + Pydantic
- SQLAlchemy 2.x
- Alembic
- JWT (ex.: python-jose)
- bcrypt
- PostgreSQL
- pytest
- Docker / Docker Compose
- Env vars (12-factor)

### 6.5 Modelagem e Evolução do Banco
- Migrations versionadas via Alembic.
- Constraints no banco para regras críticas (unicidade, datas).
- Evitar triggers; regra de negócio fica nos casos de uso.
- Preparar índices para filtros principais.

### 6.6 LGPD, Auditoria e Governança de Dados
- Privacy-by-design: `User` vs `CandidateProfile`.
- Admin institucional: `User.institution_id`.
- Consentimento contextual: `Consent` vinculado à `Application`.
- Auditoria: `AuditEvent` (append-only).
- Acesso: `DataAccessLog` (accountability).

### 6.7 Observabilidade e Logging
- Logging estruturado (JSON) por request.
- `request_id` para correlação.
- Registro consistente de erros, auditorias e acessos.

### 6.8 Tratamento de Erros
- Envelope de erro padrão:
  - `code`, `message`, `details?`, `request_id`
- HTTP status codes consistentes:
  - `400`, `401`, `403`, `404`, `409`, `422`, `500`
- Erros de domínio tratados na Application Layer e mapeados na Presentation Layer.

---

## 7. Requisitos Não-Funcionais e como a arquitetura atende

### RNF-001 Segurança / LGPD
- Separação `User` x `CandidateProfile`
- Soft delete para histórico/retenção
- `AuditEvent` e `DataAccessLog`
- RBAC + autorização contextual (institution + consent)

### RNF-002 Escalabilidade (100K+ simultâneos)
- Paginação obrigatória
- Índices em filtros (institution, type, status)
- JWT stateless (escala horizontal)

### RNF-003 Manutenibilidade / Flexibilidade
- Camadas bem definidas
- Use cases testáveis
- Domínio desacoplado

### RNF-004 Observabilidade
- `request_id` e logging estruturado
- Auditoria de mudanças e acessos

---

## 8. Decisões técnicas

## Architecture Decision Records (ADRs)

| ID | Arquivo | Título | Objetivo da Decisão |
|----|--------|--------|---------------------|
| ADR-001 | [3_adr_001_layers.md](./3_adr_001_layers.md) | Separação de Camadas | Definir a arquitetura em camadas (Presentation, Application, Domain e Infrastructure) para reduzir acoplamento, facilitar testes e suportar evolução do sistema. |
| ADR-002 | [4_adr_002_database.md](./4_adr_002_database.md) | Escolha do Banco de Dados | Justificar o uso de PostgreSQL como banco relacional principal, considerando integridade, relacionamentos complexos e requisitos de auditoria e LGPD. |
| ADR-003 | [5_adr_003_auth.md](./5_adr_003_auth.md) | Autenticação e Autorização | Definir JWT como mecanismo de autenticação e RBAC como estratégia de autorização para controle de acesso seguro e escalável. |
| ADR-004 | [6_adr_004_api.md](./6_adr_004_api.md) | Padrão de API | Adotar API RESTful como padrão de integração, favorecendo simplicidade, interoperabilidade e manutenibilidade. |
| ADR-005 | [7_adr_005_versioning.md](./7_adr_005_versioning.md) | Versionamento de API | Estabelecer versionamento por URL (`/api/v1`) para permitir evolução controlada e compatibilidade entre múltiplos clientes. |
| ADR-006 | [8_adr_006_lgpd.md](./8_adr_006_lgpd.md) | LGPD Logging e Auditoria | Definir estratégia de auditoria, rastreabilidade e minimização de dados pessoais para conformidade com a LGPD. |
| ADR-007 | [9_adr_007_delete_strategy.md](./9_adr_007_delete_strategy.md) | Estratégia de Exclusão de Dados | Definir o uso de *soft delete* como padrão para preservar histórico, integridade referencial e accountability, com *hard delete* restrito a cenários controlados. |
| ADR-008 | [10_adr_008_api_conventions.md](./10_adr_008_api_conventions.md) | Convenções de API | Estabelecer padrões consistentes para endpoints, payloads, paginação, filtros, status codes e envelope de erros, garantindo previsibilidade, integração facilitada e menor custo de manutenção. |
| ADR-009 | [11_adr_009_observability.md](./11_adr_009_observability.md) | Observabilidade | Definir estratégia mínima de logging estruturado, métricas, correlação de requisições e preparo para tracing, visando diagnóstico rápido, operação segura e escalabilidade com time reduzido. |

---

| **Anterior** | **Próximo** |
|-----------------|---------------|
| [Captura de Requisitos](./1_requirements_capture.md) | [ADR-001: Separação de Camadas](./3_adr_001_layers.md) |
