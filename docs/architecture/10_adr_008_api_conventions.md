# ADR-008: Convenções de API (REST) — Padrões de Request/Response e Erros

**Status:** Accepted  
**Data:** 2026-01-27  
**Contexto:** Plataforma de gestão de ofertas acadêmicas (cursos, bolsas, estágios) consumida por múltiplos clientes (web, mobile e integrações). O time de backend é pequeno (2–3 pessoas), requisitos mudam com frequência e a API deve ser clara, consistente e autoexplicativa. O desafio exige padronização de respostas, status codes, paginação, filtros, versionamento e um tratamento de erros coerente.

---

## Decision

Adotar convenções consistentes para endpoints REST, payloads, paginação, filtros, erros, autenticação e versionamento, conforme abaixo.

### 1) Estilo de endpoints e nomes

- Base path: `/api/v1`
- Recursos no plural: `/offers`, `/applications`, `/users`, `/institutions`
- Identificador em path: `/offers/{id}`
- Sub-recursos: `/users/{id}/applications`
- Ações específicas (não-CRUD) como sub-rotas:
  - Atualização de status: `POST /api/v1/applications/{id}/status`

### 2) Regras de request/response (JSON)

- Content-Type padrão: `application/json; charset=utf-8`
- Requests de criação/atualização usam JSON body.
- Respostas retornam apenas o necessário para o cliente, evitando dados sensíveis por padrão (LGPD).
- Datas em ISO 8601 (UTC quando aplicável).

### 3) Versionamento

- Versionamento **URL-based**: `/api/v1/...`
- Mudanças compatíveis (backward compatible) não incrementam versão major.
- Mudanças breaking exigem nova versão (`/api/v2`).

### 4) Paginação e ordenação

- Listas usam `limit` e `offset`:
  - `GET /api/v1/offers?limit=20&offset=0`
- Defaults:
  - `limit=20`
  - `max_limit=100`
  - `offset=0`
- Resposta de lista retorna:
  - `items`: lista de recursos
  - `pagination`: metadados mínimos (limit, offset, total)

### 5) Filtros

- Filtros via query params, sem inventar DSL:
  - `institution_id`
  - `type` (ex: `course`, `scholarship`)
  - `status`
- Exemplo:
  - `GET /api/v1/offers?institution_id=...&type=course&status=published&limit=20&offset=0`

### 6) Contrato de erros (envelope único)

Todos os erros retornam o mesmo formato:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": [
      { "field": "optional_string", "reason": "optional_string" }
    ],
    "request_id": "string"
  }
}
````

- `code`: identificador estável para tratamento do cliente (ex: `VALIDATION_ERROR`, `UNAUTHORIZED`)
- `message`: mensagem legível (sem expor detalhes internos)
- `details`: lista opcional de violações/erros por campo
- `request_id`: id de correlação para debug e auditoria

### 7) Status codes (padrão mínimo)

- `200 OK`: leitura/atualização bem-sucedida (quando aplicável)
- `201 Created`: criação bem-sucedida
- `204 No Content`: delete bem-sucedido (quando não retornar body)
- `400 Bad Request`: payload inválido, parâmetros inválidos
- `401 Unauthorized`: token ausente/inválido
- `403 Forbidden`: autenticado, mas sem permissão (RBAC)
- `404 Not Found`: recurso inexistente
- `409 Conflict`: conflito de regra (ex: aplicar 2x na mesma offer)
- `422 Unprocessable Entity`: validação semântica de dados (ex: datas conflitantes)
- `429 Too Many Requests`: rate limit
- `500 Internal Server Error`: erro inesperado (sem vazar stacktrace)

### 8) Autenticação e autorização (headers)

- Token JWT via header:
    > Authorization: Bearer <token>

- Endpoints protegidos devem retornar 401 quando não autenticado.
- RBAC:
    - `403` quando usuário autenticado não tem role necessária (ex: somente admin cria offers).

### 9) Idempotência e segurança de operações

- PUT /resource/{id}: idempotente (substitui/atualiza recurso)
- POST para ações (ex: status) pode ser não-idempotente; quando possível, deve validar transições para evitar estados inválidos.
- Em caso de reprocessamento/duplicidade:
    - regras de negócio garantem consistência (ex: não permitir apply 2x na mesma offer).

### 10) Correlation ID e logging

- A API deve gerar ou propagar um `request_id` por request.

- `request_id` deve aparecer:
    - no envelope de erro
    - nos logs do servidor

- Nunca logar dados sensíveis (LGPD) em nível INFO/ERROR; dados pessoais devem ser minimizados/masked.

--- 

## Justificativa

- Consistência para múltiplos clientes: reduz custo de integração e bugs de front/mobile.
- Time pequeno e código autoexplicativo: padrão único evita decisões repetidas e divergentes.
- Evolução com mudanças frequentes: convenções claras minimizam impacto de novas features.
- Operação e suporte: `request_id` e envelope de erro padronizado facilitam troubleshooting.
- LGPD: respostas e logs minimizam exposição de dados, alinhando segurança e compliance.

---

## Consequências

### Positivas

- Clientes implementam integrações com menor ambiguidade.
- Facilita testes automatizados (contratos previsíveis).
- Padroniza tratamento de erros e melhora observabilidade.

### Negativas / Trade-offs

- Exige disciplina do time para manter o padrão.
- Pode haver necessidade de refatorar endpoints antigos se surgirem inconsistências.
- Envelope de erro exige mapeamento cuidadoso de exceções internas → códigos estáveis.

---

## Exemplos

### 1) Listagem com paginação

Request
`GET /api/v1/offers?limit=20&offset=0`

**Response (200)**
```json
{
  "items": [
    { "id": "uuid", "title": "string", "type": "course", "status": "published" }
  ],
  "pagination": { "limit": 20, "offset": 0, "total": 123 }
}
```

### 2) Erro de validação

**Response (422)**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input.",
    "details": [
      { "field": "application_deadline", "reason": "must be after publication_date" }
    ],
    "request_id": "req_01HXYZ..."
  }
}
```

### 3) Conflito (aplicar 2x na mesma offer)

**Response (409)**
```json
{
  "error": {
    "code": "APPLICATION_ALREADY_EXISTS",
    "message": "Candidate already applied to this offer.",
    "details": [],
    "request_id": "req_01HXYZ..."
  }
}
```

---

| **Anterior** | **Próximo** |
|---|---|
| [ADR-007: Estratégia de Exclusão de Dados](./9_adr_007_delete_strategy.md) | [ADR-009: Observabilidade](./11_adr_009_observability.md) |