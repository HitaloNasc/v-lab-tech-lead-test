# Design Arquitetural — Plataforma de Gestão de Ofertas e Candidaturas (V-LAB)

**Data:** 26/01/2026  
**Autor:** Hítalo Nascimento  
**Status:** Rascunho (baseado na captura de requisitos e modelo conceitual)
**Referências:**
- [Captura de Requisitos](./requirements-capture.md)
- [Modelo Conceitual de Dados (PlantUML)](./diagrams/concept-data-model.puml)

## 1. Visão Geral

### 1.1 Contexto
Plataforma para universidades brasileiras gerenciarem **ofertas acadêmicas** (cursos, bolsas, estágios) e **candidaturas**, com consumo por múltiplos clientes (web/mobile/integrações). O sistema deve operar com **dados sensíveis**, exigindo conformidade com LGPD, além de escalar para **100K+ usuários simultâneos**, mantendo manutenibilidade (time backend pequeno).

### 1.2 Objetivo
Fornecer uma API versionada (v1) que suporte:
- Autenticação e autorização (RBAC)
- CRUD de ofertas com paginação e filtros
- Criação e gerenciamento de candidaturas com regras de negócio
- Rastreabilidade (auditoria de alterações e acessos) para LGPD

### 1.3 Escopo do núcleo funcional
Inclui:
- User registration + login + JWT
- CRUD Offers
- Applications (criar, listar por usuário, atualizar status)
- Regras: unicidade de candidatura por oferta e validação de prazo
- RBAC: apenas admin cria oferta
- LGPD logging (recomendado no design): auditoria de alteração + acesso

---

## 2. Modelo Conceitual de Dados

### 2.1 Entidades principais (conceitual)
- **[Institution]**: Representa a instituição/universidade proprietária das ofertas e programas. Centraliza o “dono” institucional do catálogo e pode servir como chave de particionamento lógico (multi-instituição).

- **[Program]**: Representa programas vinculados a uma `institution` (ex.: programa de pós, edital, trilha), permitindo organizar ofertas por contexto institucional.

- **[Offer]**: Oferta acadêmica (curso, bolsa, estágio) publicada por uma `institution` e opcionalmente associada a um `program`. Contém tipo, status e janelas de publicação/candidatura (com regra `application_deadline > publication_date`).

- **[User]**: Identidade autenticável (cadastro/login) com credenciais (hash de senha) e trilha de ciclo de vida (soft delete + motivo). Serve como base para autorização (papéis) e como referência do titular (data subject) e do agente (actor) em registros de auditoria.

- **[Role]**: Catálogo de perfis de acesso (ex.: `admin`, `user/candidate`) usado para aplicar autorização baseada em papéis (RBAC).

- **[UserRole]**: Tabela de junção N:N entre `user` e `role`, permitindo que um usuário possua múltiplos papéis (e.g., admin + outro perfil) e suportando evolução futura de permissões.

- **[CandidateProfile]**: Perfil do candidato com dados pessoais separados de `User` (privacy-by-design). Vinculado 1:1 ao `user`. Pode conter campos adicionais (ex.: CPF, data de nascimento) e aplica soft delete para suportar políticas LGPD. **Não armazena consentimento por candidatura**; o consentimento contextual foi movido para `Consent`.

- **[Application]**: Candidatura de um candidato (`candidate_profile`) para uma `offer`, com status do processo seletivo. Impõe unicidade por par (`candidate_profile_id`, `offer_id`) para evitar candidatura duplicada e deve respeitar regras de prazo (não permitir apply após `application_deadline`).

- **[Consent]**: Registro de consentimento **contextual e versionado** associado a uma candidatura (`application`) e ao titular (`user`). Permite registrar quando o consentimento foi dado (`consented_at`), qual versão de termos/política foi aceita (`terms_version`) e o **escopo** do consentimento (`scope`, p.ex. aceite de termos da candidatura, compartilhamento de dados, etc.). Suporta revogação sem perda de histórico (`revoked_at`) e pode guardar evidências técnicas (IP, user agent, hash/assinatura do texto exibido), reforçando rastreabilidade e accountability. (Recomendável garantir unicidade por `application_id + scope + terms_version`.)

#### LGPD / Audit (opcional na implementação inicial, recomendado no design)

- **[AuditEvent]**: Registro append-only de auditoria de alterações. Captura quem executou (`actor_user_id`), quando (`occurred_at`), qual ação (`action`) e qual registro foi afetado (`entity_type` + `entity_id`), além de contexto técnico (IP, user agent, request id) e diffs (`before`/`after`) para rastreabilidade de mudanças em dados sensíveis e estados críticos (ex.: status de candidatura, mudanças em perfil, criação/alteração de ofertas, registros de consentimento).

- **[DataAccessLog]**: Registro de auditoria de acesso/leitura a dados (principalmente pessoais). Captura quem acessou (`actor_user_id`), quando (`accessed_at`), de quem são os dados (`data_subject_user_id`, quando aplicável), qual recurso foi consultado (`resource`/`resource_id`), finalidade (`purpose`) e contexto técnico (IP, user agent, request id). Ideal para rastrear acessos administrativos, especialmente quando o ator não é o titular, e suportar accountability LGPD.


### 2.2 Regras e constraints no modelo de dados

As regras e constraints a seguir derivam diretamente dos requisitos funcionais (RFs) e garantem consistência, integridade e conformidade legal (LGPD) no modelo de dados.

- **Unicidade de candidatura (RF-009):**  
  A entidade `Application` deve ser única por par (`candidate_profile_id`, `offer_id`), impedindo que um mesmo candidato realize múltiplas candidaturas para a mesma oferta.  
  *Implementação sugerida:* `UNIQUE (candidate_profile_id, offer_id)`.

- **Integridade temporal da oferta (RF-010):**  
  A entidade `Offer` deve respeitar a regra `application_deadline > publication_date`, evitando janelas de candidatura inválidas ou conflitantes.  
  *Implementação sugerida:* constraint de banco (`CHECK`) ou validação obrigatória no caso de uso de criação/atualização de oferta.

- **Validação de prazo de candidatura (RF-011):**  
  Não é permitido criar uma `Application` para uma `Offer` cujo `application_deadline` já tenha expirado no momento da requisição.  
  *Implementação sugerida:* validação no serviço/caso de uso de criação de candidatura, com base na data/hora atual do sistema.

- **Controle de acesso por papel (RBAC) (RF-005):**  
  Apenas usuários com papel `admin` podem criar, atualizar ou remover `Offer`.  
  *Implementação sugerida:* validação no nível de aplicação (middleware/guard), utilizando as entidades `Role` e `UserRole`. O modelo de dados suporta essa regra ao permitir múltiplos papéis por usuário.

- **Consistência de autenticação e autorização (RF-001, RF-002):**  
  A entidade `User` deve armazenar apenas o hash da senha (ex.: bcrypt), nunca a senha em texto puro. A emissão de JWT depende da associação correta entre `User` e `Role`, refletida no modelo por meio de `UserRole`.

- **Separação de identidade e dados pessoais (privacy-by-design):**  
  Dados pessoais do candidato devem residir exclusivamente em `CandidateProfile`, mantendo a entidade `User` focada apenas em autenticação e autorização. Essa separação reduz exposição indevida e facilita atendimento a solicitações LGPD.

- **Consentimento contextual e versionado (RF-006, RF-013):**  
  Cada candidatura (`Application`) deve possuir ao menos um registro de `Consent` válido, associado ao titular (`User`) e à candidatura específica. O consentimento deve registrar versão de termos, data/hora do aceite e escopo.  
  *Implementação sugerida:* constraint lógica exigindo a existência de `Consent` para `Application` ativa, com unicidade recomendada por (`application_id`, `scope`, `terms_version`).

- **Soft delete e retenção histórica (LGPD):**  
  As entidades principais (`User`, `CandidateProfile`, `Offer`, `Application`) utilizam soft delete (`deleted_at`) para preservar histórico, integridade referencial e rastreabilidade, evitando remoções físicas diretas.

- **Auditoria de alterações (RF-013):**  
  Alterações relevantes em entidades sensíveis (ex.: `Offer`, `Application`, `CandidateProfile`, `Consent`) devem gerar registros em `AuditEvent`, em modo append-only, garantindo rastreabilidade completa de quem alterou, quando e o que foi alterado.

- **Auditoria de acesso a dados pessoais (RF-013):**  
  Leituras de dados pessoais, especialmente quando realizadas por usuários diferentes do titular, devem ser registradas em `DataAccessLog`, incluindo ator, titular, finalidade e contexto técnico (IP, user agent).

Essas regras garantem que o modelo de dados suporte corretamente os fluxos funcionais definidos, mantendo consistência técnica, segurança, governança de acesso e aderência às exigências da LGPD.


---

## 3. Arquitetura de Camadas

### 3.1 Motivação
A separação em camadas reduz acoplamento, facilita testes, suporta mudanças frequentes de requisitos e melhora a manutenibilidade em um time pequeno.

### 3.2 Visão em camadas (alto nível)
![alt text](./diagrams/layers_simple.png)

### 3.3 Responsabilidades por camada
#### Presentation Layer (API)

Responsável por:

- Definir rotas e contratos HTTP (v1)
- Autenticação por JWT (guard/decorator)
- Validação de input via schemas (Pydantic)
- Mapeamento de erros para HTTP status + payload padronizado
- Paginação e filtros de listagem
- CORS e rate limiting (por IP)

*Não deve conter regra de negócio (apenas orquestração e validação de entrada/saída).*

#### Application Layer (Use Cases)

Responsável por:

- Orquestrar regras de negócio entre entidades e repositórios
- Aplicar validações que dependem de estado e persistência (ex.: deadline, unicidade)
- Emitir eventos de auditoria (AuditEvent) e logs de acesso (DataAccessLog) quando aplicável
- Controlar transações (quando necessário)

Exemplos de casos de uso:

- `RegisterUser`
- `LoginUser`
- `CreateOffer` (exige role admin)
- `ListOffers` (paginação/filtros)
- `CreateApplication` (unicidade + deadline)
- `UpdateApplicationStatus`

#### Domain Layer (Domínio)

Responsável por:

- Definir entidades e invariantes (Offer, Application, CandidateProfile etc.)
- Representar estados e valores do domínio (ex.: enums)
- Regras puras e invariantes locais (ex.: datas válidas para Offer, status permitidos)
- O domínio não depende de HTTP nem de banco.

#### Infrastructure Layer (Infra)

Responsável por:

- Persistência (PostgreSQL via ORM)
- Implementação de repositórios
- Integrações e utilitários técnicos (hash de senha, JWT provider, rate limit store se necessário)
- Migrações (Alembic)
- Observabilidade (logging estruturado)

---

## 4. Contratos de API (v1)
### 4.1 Autenticação e segurança

- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- Autorização via RBAC (roles em UserRole)
- Endpoints protegidos com guard/decorator `@require_auth`
- Rate limiting simples: `max X req/min` por IP (configurável)

### 4.2 Offers

- POST `/api/v1/offers` (admin-only)
- GET `/api/v1/offers?limit=20&offset=0`
- GET `/api/v1/offers/{id}`
- PUT `/api/v1/offers/{id}`
- DELETE `/api/v1/offers/{id}`
- Filtros: por institution, type, status

### 4.3 Applications

- POST `/api/v1/applications`
- GET `/api/v1/users/{id}/applications`
- POST `/api/v1/applications/{id}/status`

Validações obrigatórias no caso de uso:
- Unicidade por (candidate_profile_id, offer_id)
- Deadline válido (não aplicar para oferta expirada)

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
- `CANDIDATE_PROFILE_UPDATED`
- `USER_SOFT_DELETED`

Campos principais:

- `occurred_at`, `actor_user_id`, `action`, `entity_type`, `entity_id`, `before`, `after`, `request_id`

Boas práticas:

- Registrar apenas campos relevantes (minimização)
- Evitar dados pessoais completos em before/after quando não necessários

### 5.3 DataAccessLog (leitura)

Registrar acessos a recursos com dados pessoais, especialmente quando:

- ator (admin) acessa dados de outro titular (candidato)
- endpoints expõem CandidateProfile/Applications

Campos principais:

- `accessed_at`, `actor_user_id`, `data_subject_user_id`, `resource`, `purpose`, `request_id`

---

## 6. Decisões Técnicas Fundamentais

### 6.1 API: REST (versionada)

- Arquitetura REST atende de forma adequada operações CRUD, fluxos de candidatura e integrações futuras (web, mobile, terceiros).
- Versionamento explícito via URL (`/api/v1/...`) garante estabilidade para clientes existentes e permite evolução controlada da API sem breaking changes.
- Uso consistente de verbos HTTP (`GET`, `POST`, `PUT/PATCH`, `DELETE`) e códigos de status semânticos.


### 6.2 Autenticação e Autorização: JWT + RBAC

- Autenticação baseada em **JWT (JSON Web Token)** para comunicação stateless entre cliente e API.
- Tokens carregam identificação do usuário e seus papéis, reduzindo consultas repetidas ao banco.
- **RBAC (Role-Based Access Control)** aplicado para restringir operações sensíveis (ex.: apenas `admin` pode criar/atualizar/deletar `Offer`).
- Modelo de dados (`User`, `Role`, `UserRole`) suporta múltiplos papéis por usuário e evolução futura de permissões.


### 6.3 Banco de Dados: PostgreSQL

**Justificativa:**

- Suporte completo a **ACID**, constraints (`UNIQUE`, `CHECK`, `FOREIGN KEY`) e integridade referencial.
- Excelente desempenho para consultas com filtros, ordenação e paginação (uso de índices).
- Tipos avançados como `UUID`, `timestamptz`, `citext`, `jsonb` e `inet` adequados ao domínio.
- Uso de `jsonb` para auditoria (`before` / `after`) sem perda de flexibilidade.
- Adequado para estratégias de soft delete e retenção histórica exigidas pela LGPD.


### 6.4 Stack Tecnológica

- **Linguagem:** Python 3.x
- **Framework Web:** FastAPI  
  - Tipagem explícita
  - Validação automática de payloads (Pydantic)
  - OpenAPI/Swagger nativo
- **ORM / Mapeamento:** SQLAlchemy 2.x
- **Migrations:** Alembic
- **Autenticação:** JWT (ex.: `python-jose`)
- **Hash de senha:** bcrypt
- **Banco de dados:** PostgreSQL
- **Testes:** pytest
- **Containerização:** Docker / Docker Compose
- **Configuração:** Variáveis de ambiente (12-factor app)


### 6.5 Modelagem e Evolução do Banco

- Migrations versionadas e reproduzíveis via Alembic.
- Uso de constraints no banco para reforçar regras críticas (unicidade, datas).
- Evitar lógica de negócio complexa em triggers; priorizar regras explícitas nos casos de uso.
- Estrutura preparada para multi-instituição e crescimento do volume de dados.


### 6.6 LGPD, Auditoria e Governança de Dados

- **Privacy-by-design:** separação entre identidade (`User`) e dados pessoais (`CandidateProfile`).
- **Consentimento explícito e contextual:** entidade `Consent` vinculada à `Application`.
- **Auditoria de alterações:** `AuditEvent` em modo append-only.
- **Auditoria de acessos:** `DataAccessLog` para leituras de dados pessoais.
- Suporte a accountability, rastreabilidade e futuras solicitações de titulares (ex.: acesso, correção, exclusão lógica).


### 6.7 Observabilidade e Logging

- Logging estruturado (JSON) por request.
- Correlação de logs via `request_id`.
- Registro consistente de erros, auditorias e acessos sensíveis.
- Preparação para integração futura com ferramentas de observabilidade (ex.: OpenTelemetry, ELK, Grafana).


### 6.8 Tratamento de Erros

- Payload de erro padronizado, contendo:
  - `code`: identificador do erro
  - `message`: descrição amigável
  - `details`: informações adicionais (opcional)
  - `request_id`: correlação para debug
- Uso consistente de HTTP status codes (`400`, `401`, `403`, `404`, `409`, `422`, `500`).
- Erros de domínio tratados no nível de aplicação, com m


Essas decisões técnicas estabelecem uma base sólida para evolução do sistema, priorizando clareza arquitetural, segurança, conformidade legal e facilidade de manutenção.

---

## 7. Requisitos Não-Funcionais e como a arquitetura atende
### RNF-001 Segurança / LGPD

- Separação User x CandidateProfile (privacy-by-design)
- Soft delete para histórico e retenção
- AuditEvent e DataAccessLog (accountability)
- Controle de acesso por RBAC

### RNF-002 Escalabilidade (100K+ simultâneos)

- Paginação obrigatória em listagens
- Índices nos filtros mais usados (institution, type, status)
- Design stateless com JWT (facilita escala horizontal) 

### RNF-003 Manutenibilidade / Flexibilidade

- Camadas bem definidas
- Use cases claros e testáveis
- Domínio desacoplado de frameworks

### RNF-004 Observabilidade (opcional)

- request_id para correlação
- logging estruturado
- auditoria de mudanças e acessos

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
