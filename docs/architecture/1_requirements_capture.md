# Captura de Requisitos — Desafio técnico V-LAB - Líder em Desenvolvimento

**Data:** 26/01/2026  
**Responsável:** Hítalo Nascimento  
**Status:** Rascunho

---

## 1. Contexto e Objetivo

- **Problema a resolver:** Desenvolver uma plataforma de gestão de ofertas acadêmicas para universidades brasileiras.
- **Objetivo:** Centralizar a gestão de ofertas acadêmicas e candidaturas, garantindo controle de acesso, conformidade com LGPD e escalabilidade.
- **Público-alvo:** Universidades (administradores institucionais) e candidatos.
- **Métricas de sucesso:**  
  - Número de ofertas publicadas  
  - Número de candidaturas processadas  
  - Tempo médio de resposta da API  

---

## 2. Requisitos Funcionais (RF)

| ID | Domínio | Descrição |
|---|---|---|
| RF-001 | Auth | Cadastro de usuário com hash de senha (bcrypt). |
| RF-002 | Auth | Login e emissão de JWT. |
| RF-003 | Offer | CRUD de Offers: criar, listar (com paginação), obter por ID, atualizar e deletar (soft delete). |
| RF-004 | Offer | Listagem de offers com filtros por `institution`, `type` e `status`. |
| RF-005 | Offer | Apenas usuários com role `admin` podem criar ou editar offers. |
| RF-006 | Application | Criar candidatura (`Application`) para uma offer. |
| RF-007 | Application | Listar candidaturas do próprio usuário (`GET /users/{id}/applications`). |
| RF-008 | Application | Atualizar status da candidatura (restrito a admin da instituição proprietária da offer). |
| RF-009 | Application | Não permitir candidatura duplicada para a mesma offer. |
| RF-010 | Application | Garantir que `application_deadline > publication_date`. |
| RF-011 | Application | Impedir candidatura para offers expiradas ou fechadas. |
| RF-012 | Institution | Gerenciar instituições e seus programas associados. |
| RF-013 | LGPD | Registrar auditoria de alterações e acessos a dados pessoais. |
| RF-014 | CandidateProfile | Leitura do perfil do candidato permitida apenas ao próprio usuário ou a admins da instituição associada **com consentimento válido**. |
| RF-015 | Consent | Validar consentimento ativo antes de permitir acesso administrativo a dados pessoais. |

---

## 3. Requisitos Não-Funcionais (RNF)

| ID | Categoria | Descrição |
|---|---|---|
| RNF-001 | Segurança | Conformidade com LGPD: minimização, controle de acesso, rastreabilidade e retenção. |
| RNF-002 | Escalabilidade | Suportar 100K+ usuários simultâneos com paginação e índices adequados. |
| RNF-003 | Manutenibilidade | Arquitetura flexível, separação clara de camadas e baixo acoplamento. |
| RNF-004 | Observabilidade | Logging estruturado e rastreabilidade de ações críticas e acessos a dados pessoais. |
| RNF-005 | Manutenibilidade | Código legível, consistente e sustentável por um time pequeno (2–3 pessoas). |

---

## 4. Dados e Validações

### 4.1 Entidades Principais

- **Institution**: Instituição proprietária das ofertas e programas.
- **Program**: Programas vinculados a uma instituição.
- **Offer**: Oferta acadêmica publicada por uma instituição.
- **User**: Identidade autenticável, associada opcionalmente a uma instituição.
- **Role**: Papéis de acesso (`admin`, `candidate`).
- **UserRole**: Associação N:N entre usuários e papéis.
- **CandidateProfile**: Dados pessoais do candidato (privacy-by-design).
- **Application**: Candidatura de um candidato a uma offer.
- **Consent**: Registro de consentimento contextual e versionado.
- **AuditEvent** *(opcional)*: Auditoria de alterações.
- **DataAccessLog** *(opcional)*: Auditoria de leitura de dados pessoais.

---

### 4.2 Atributos por Entidade

![alt text](diagrams/concept_data_model.png)

#### **Institution**
- `id` (UUID, PK)
- `name` (text, obrigatório)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)

#### **Program**
- `id` (UUID, PK)
- `institution_id` (UUID, FK → Institution.id)
- `name` (text)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)

#### **Offer**
- `id` (UUID, PK)
- `institution_id` (UUID, FK → Institution.id)
- `program_id` (UUID, FK → Program.id, opcional)
- `title` (text)
- `description`(text)
- `type` (enum: course | scholarship | internship)
- `status` (enum: active | inactive | closed)
- `publication_date` (timestamptz)
- `application_deadline` (timestamptz)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)

#### **User**
- `id` (UUID, PK)
- `email` (citext/text, único)
- `hashed_password` (text)
- `institution_id` (UUID, FK → Institution.id, **opcional**)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)

> **Regra:**  
> - Usuários com role `admin` **devem** possuir `institution_id` preenchido.  
> - Usuários candidatos **não devem** possuir `institution_id`.

#### **Role**
- `id` (UUID, PK)
- `name` (text, único)
- `description`(text, opcional)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)

#### **UserRole**
- `user_id` (UUID, FK → User.id)
- `role_id` (UUID, FK → Role.id)
- `created_at` (timestamptz)

#### **CandidateProfile**
- `id` (UUID, PK)
- `user_id` (UUID, FK → User.id, único)
- `full_name` (text)
- `date_of_birth` (date, opcional*)
- `cpf` (text, opcional*)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)

\* Campos opcionais não explicitados no enunciado.

#### **Application**
- `id` (UUID, PK)
- `candidate_profile_id` (UUID, FK → CandidateProfile.id)
- `offer_id` (UUID, FK → Offer.id)
- `status` (enum)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `deleted_at` (timestamptz)
- `deleted_by` (UUID, FK → User.id, opcional)
- `deletion_reason` (text, opcional)
- **Regra:** unicidade `(candidate_profile_id, offer_id)`

#### **Consent**
- `id` (UUID, PK)
- `user_id` (UUID, FK → User.id)
- `application_id` (UUID, FK → Application.id)
- `scope` (text)
- `terms_version` (text)
- `consented_at` (timestamptz)
- `revoked_at` (timestamptz, opcional)
- `ip` (inet, opcional)
- `user_agent` (text, opcional)
- `evidence_hash` (text, opcional)
- `created_at` (timestamptz)
- **Regra:** unicidade `(application_id, scope, terms_version)`

---

### 4.3 Regras de Autorização e Acesso a Dados Sensíveis

#### CandidateProfile
- Pode ser lido:
  - Pelo próprio usuário titular; ou
  - Por usuários com role `admin` **desde que**:
    - `user.institution_id = offer.institution_id`; e
    - Exista consentimento ativo (`revoked_at IS NULL`) associado à candidatura.
- Não pode ser listado em massa fora do contexto de candidatura.
- Pode ser atualizado apenas pelo próprio titular.

#### Application
- Candidatos visualizam apenas suas próprias candidaturas.
- Admins visualizam apenas candidaturas de offers da sua instituição.
- Alterações de status exigem role `admin` e devem ser auditadas.

#### Consent
- Consentimentos são imutáveis após criação.
- Apenas `revoked_at` pode ser atualizado.
- Consentimentos revogados não autorizam novos acessos.

#### Auditoria
- Todo acesso administrativo a dados pessoais gera `DataAccessLog`.
- Alterações relevantes geram `AuditEvent`.
- Logs são append-only.

---

## Navegação

| **Anterior** | **Próximo** |
|-------------|-------------|
| [Início](./README.md) | [Design Arquitetural](./2_design.md) |
