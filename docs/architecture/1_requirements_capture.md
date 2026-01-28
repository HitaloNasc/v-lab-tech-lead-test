# Captura de Requisitos — Desafio técnico V-LAB - Líder em desenvolvimento

**Data:** 26/01/2026  
**Responsável:** Hítalo Nascimento  
**Status:** Rascunho

---

## 1. Contexto e Objetivo

- **Problema a resolver:** Desenvolver uma plataforma de gestão de ofertas acadêmicas para universidades brasileiras.
- **Objetivo**: Centralizar a gestão de ofertas acadêmicas e candidaturas, com controle de acesso e escalabilidade.
- **Público-alvo**: Universidades (admins) e candidatos.
- **Métricas**: nº de ofertas publicadas, candidaturas processadas, tempo de resposta da API.

---

## 2. Requisitos Funcionais (RF)

| ID | Feature | Descrição |
|---|---|---|
| RF-001 |  Auth | Cadastro de usuário com hash de senha (bcrypt). |
| RF-002 |  Auth | Login e emissão de JWT (impacta ao menos “usuário”, “roles”). |
| RF-003 |  Offer | CRUD de Offers: criar, listar (com paginação), obter por ID, atualizar, deletar. |
| RF-004 |  Offer | Listagem com filtros por institution, type (course/scholarship) e status. |
| RF-005 | Offer | Regra: apenas `admin` pode criar `offer` (RBAC). |
| RF-006 |  Application | Criar candidatura. |
| RF-007 |  Application | Listar candidaturas do usuário:  `GET /users/{id}/applications`. |
| RF-008 |  Application | Atualizar status da candidatura. |
| RF-009 |  Application | Regra: não permitir aplicar 2x na mesma offer; verificar deadline. |
| RF-010 | Application | Regra: application_deadline > publication_date (Sem datas conflitantes). |
| RF-011 | Application | Regra: candidato não pode aplicar para offer expirada. |
| RF-012 | Institution | Gerenciar instituições e seus programas associados, permitindo associação às offers. |
RF-013 | LGPD | Registrar alterações e acessos a dados pessoais para fins de auditoria.
<!-- 
| RF-014 |  |  |
| RF-015 |  |  | 
-->

---

## 3. Requisitos Não-Funcionais (RNF)

Sugestão: RNF-001, RNF-002...

| ID | Categoria | Descrição |
|---|---|---|
| RNF-001 | Segurança | Dados sensíveis, LGPD compliance obrigatório (impacta: minimização, rastreabilidade, controle de acesso, retenção/eliminação). |
| RNF-002 | Escalabilidade | Escalar para 100K+ usuários simultânios (impacta: índices, paginação, padrões de consulta) |
| RNF-003 | Manutenibilidade | Arquitetura flexível para acomodar mudanças frequentes de requisitos, com separação clara de camadas. |
| RNF-004 | Observabilidade | O sistema deve possuir logging estruturado e rastreabilidade de ações relevantes, incluindo alterações de estado e acesso a dados pessoais, de forma a suportar auditoria, diagnóstico de falhas e requisitos de LGPD (accountability). |
| RNF-005 | Manutenibilidade | O sistema deve ser projetado para fácil manutenção por um time reduzido (2–3 pessoas), com código autoexplicativo, separação clara de responsabilidades, padrões consistentes e baixo acoplamento entre camadas. |
<!--
| RNF-006 |  |  |
-->
<!-- Categorias comuns: Performance, Segurança, Observabilidade, Usabilidade/Acessibilidade, Confiabilidade, Manutenibilidade, Compatibilidade. -->

---

## 4. Dados e Validações

### 4.1 Entidades principais 

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

### 4.2 Atributos por entidade
![alt text](./diagrams/concept_data_model.png)

### 4.2 Atributos por entidade

A seguir, os principais atributos previstos no modelo conceitual, com indicação de tipo sugerido e observações de uso/regras.

#### **Institution**
- `id` *(UUID, PK)*: identificador da instituição.
- `name` *(text, obrigatório)*: nome da instituição.
- `created_at` *(timestamptz)*: data/hora de criação do registro.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: marcação de exclusão lógica (soft delete).

#### **Program**
- `id` *(UUID, PK)*: identificador do programa.
- `institution_id` *(UUID, FK → Institution.id, obrigatório)*: instituição proprietária do programa.
- `name` *(text, obrigatório)*: nome do programa.
- `created_at` *(timestamptz)*: data/hora de criação.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: exclusão lógica (soft delete).

#### **Offer**
- `id` *(UUID, PK)*: identificador da oferta.
- `institution_id` *(UUID, FK → Institution.id, obrigatório)*: instituição que publica a oferta.
- `program_id` *(UUID, FK → Program.id, opcional)*: programa ao qual a oferta pertence (quando aplicável).
- `type` *(enum)*: tipo da oferta (`course | scholarship | internship`).
- `status` *(enum)*: estado da oferta (`active | inactive | closed`).
- `publication_date` *(timestamptz, obrigatório)*: início/registro de publicação.
- `application_deadline` *(timestamptz, obrigatório)*: deadline final para candidatura (**deve ser > publication_date**).
- `created_at` *(timestamptz)*: data/hora de criação.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: exclusão lógica (soft delete).

#### **User**
- `id` *(UUID, PK)*: identificador do usuário.
- `email` *(citext/text, obrigatório, único)*: e-mail de login (case-insensitive recomendado via `citext`).
- `password_hash` *(text, obrigatório)*: hash de senha (ex.: bcrypt).
- `created_at` *(timestamptz)*: data/hora de criação.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: exclusão lógica.
- `deleted_by` *(UUID, FK → User.id, opcional)*: usuário responsável pela exclusão (em caso administrativo).
- `deletion_reason` *(text, opcional)*: justificativa/motivo da exclusão (auditoria/governança).

#### **Role**
- `id` *(UUID, PK)*: identificador do papel.
- `name` *(text, único)*: nome do papel (ex.: `admin`, `user/candidate`).
- `created_at` *(timestamptz)*: data/hora de criação.

#### **UserRole**
- `user_id` *(UUID, FK → User.id, PK)*: referência ao usuário.
- `role_id` *(UUID, FK → Role.id, PK)*: referência ao papel.
- `created_at` *(timestamptz)*: data/hora de atribuição do papel.

#### **CandidateProfile**
- `id` *(UUID, PK)*: identificador do perfil do candidato.
- `user_id` *(UUID, FK → User.id, obrigatório, único)*: vínculo 1:1 com `User`.
- `full_name` *(text, obrigatório)*: nome completo do candidato.
- `date_of_birth` *(date, opcional\*)*: data de nascimento (*marcado como não presente no enunciado*).
- `cpf` *(text, opcional\*)*: CPF (*marcado como não presente no enunciado*).
- `created_at` *(timestamptz)*: data/hora de criação.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: exclusão lógica (soft delete).

#### **Application**
- `id` *(UUID, PK)*: identificador da candidatura.
- `candidate_profile_id` *(UUID, FK → CandidateProfile.id, obrigatório)*: candidato que se inscreve.
- `offer_id` *(UUID, FK → Offer.id, obrigatório)*: oferta alvo da candidatura.
- `status` *(enum – valores a definir)*: status do processo seletivo (a ser definido conforme regra de negócio).
- `created_at` *(timestamptz)*: data/hora de criação.
- `updated_at` *(timestamptz)*: data/hora da última atualização.
- `deleted_at` *(timestamptz)*: exclusão lógica.
- *(Regra do modelo)*: unicidade por `(candidate_profile_id, offer_id)` para impedir candidatura duplicada.

#### **Consent**
- `id` *(UUID, PK)*: identificador do consentimento.
- `user_id` *(UUID, FK → User.id, obrigatório)*: titular que concedeu o consentimento.
- `application_id` *(UUID, FK → Application.id, obrigatório)*: contexto da candidatura associada.
- `scope` *(text, obrigatório)*: escopo/tipo do consentimento (ex.: `APPLICATION_TERMS`, `DATA_SHARING`, etc.).
- `terms_version` *(text, obrigatório)*: versão do termo/política aceita.
- `consented_at` *(timestamptz, obrigatório)*: data/hora do aceite.
- `revoked_at` *(timestamptz, opcional)*: data/hora de revogação (quando aplicável).
- `ip` *(inet, opcional)*: IP registrado no aceite (evidência).
- `user_agent` *(text, opcional)*: user agent registrado no aceite (evidência).
- `evidence_hash` *(text, opcional)*: hash/assinatura do conteúdo exibido (evidência).
- `created_at` *(timestamptz)*: data/hora de criação do registro.
- *(Recomendação do modelo)*: unicidade por `(application_id, scope, terms_version)`.

---

### LGPD / Audit (optional)

#### **AuditEvent**
- `id` *(UUID, PK)*: identificador do evento de auditoria.
- `occurred_at` *(timestamptz, obrigatório)*: instante do evento.
- `actor_user_id` *(UUID, FK → User.id, obrigatório)*: usuário que executou a ação.
- `action` *(text, obrigatório)*: ação executada (ex.: `OFFER_CREATED`, `APPLICATION_STATUS_CHANGED`).
- `entity_type` *(text, obrigatório)*: tipo da entidade afetada (ex.: `offer`, `application`).
- `entity_id` *(UUID, obrigatório)*: identificador do registro afetado.
- `ip` *(inet, opcional)*: IP da requisição.
- `user_agent` *(text, opcional)*: user agent da requisição.
- `request_id` *(text/uuid, opcional)*: correlação por request.
- `before` *(jsonb, opcional)*: estado anterior (quando aplicável).
- `after` *(jsonb, opcional)*: estado posterior (quando aplicável).
- *(Regra do modelo)*: append-only (não atualizar/deletar).

#### **DataAccessLog**
- `id` *(UUID, PK)*: identificador do log de acesso.
- `accessed_at` *(timestamptz, obrigatório)*: instante do acesso.
- `actor_user_id` *(UUID, FK → User.id, obrigatório)*: usuário que acessou os dados.
- `data_subject_user_id` *(UUID, FK → User.id, opcional)*: titular dos dados (quando aplicável).
- `action` *(text, obrigatório)*: tipo de ação (ex.: `READ`).
- `resource` *(text, obrigatório)*: recurso acessado (ex.: `candidate_profile`, `applications`).
- `resource_id` *(UUID, opcional)*: id do recurso acessado (quando aplicável).
- `purpose` *(text, opcional)*: finalidade declarada (ex.: suporte, análise).
- `ip` *(inet, opcional)*: IP da requisição.
- `user_agent` *(text, opcional)*: user agent da requisição.
- `request_id` *(text/uuid, opcional)*: correlação por request.


---

| **Anterior** | **Próximo** |
|-----------------|---------------|
| [Início](./README.md) | [Design Arquitetural](./2_design.md) |

