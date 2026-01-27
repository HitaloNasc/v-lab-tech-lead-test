# ADR-009: Observabilidade — Logging, Monitoring e Tracing

**Status:** Accepted  
**Data:** 2026-01-27  
**Contexto:** A plataforma de gestão de ofertas acadêmicas será consumida por múltiplos clientes (web, mobile e integrações), deve escalar para 100K+ usuários simultâneos e processa dados sensíveis (LGPD). O time de backend é pequeno (2–3 pessoas), portanto a operação do sistema precisa ser simples, com diagnóstico rápido de falhas, rastreabilidade de requisições e visibilidade de performance, sem aumentar complexidade desnecessária.

---

## Decision

Adotar uma estratégia de observabilidade mínima, consistente e pronta para produção, composta por:

1. **Logging estruturado (JSON)**
2. **Correlation ID por requisição (`request_id`)**
3. **Métricas de aplicação (RED/USE) e saúde**
4. **Tracing distribuído (preparado para OpenTelemetry)**
5. **Práticas LGPD para logs e telemetria**

---

## Details

### 1) Logging estruturado

- Formato padrão: **JSON** (um evento por linha).
- Níveis:
  - `DEBUG`: desenvolvimento/diagnóstico local (desabilitado por padrão em produção)
  - `INFO`: eventos normais (startup, request summary, jobs)
  - `WARNING`: situações anormais recuperáveis
  - `ERROR`: falhas tratadas que impactam request/operação
  - `CRITICAL`: falhas que indicam instabilidade grave
- Campos mínimos em todos os logs:
  - `timestamp`
  - `level`
  - `service` (nome do serviço)
  - `env` (dev/staging/prod)
  - `request_id`
  - `message`
- Campos recomendados para requests:
  - `http.method`, `http.path`, `http.status_code`
  - `duration_ms`
  - `client_ip` (com cuidado LGPD; preferir mascaramento/truncamento)
  - `user_id` (quando autenticado; evitar PII como email/documentos)

### 2) Correlation ID (`request_id`)

- Gerar um `request_id` por requisição, aceitando propagação quando houver:
  - Se o cliente enviar `X-Request-Id`, reutilizar; caso contrário, gerar um novo.
- Propagar `request_id` em:
  - logs de request
  - envelope de erro da API
  - header de resposta `X-Request-Id`

### 3) Padrão de logs por request

Para cada request, registrar um log resumido no fim do processamento contendo:
- método, rota, status code, duração
- `request_id`
- (opcional) tipo de erro (`error.code`) quando houver

**Não** registrar payloads completos por padrão.

### 4) Monitoramento (métricas e health)

Implementar métricas mínimas seguindo princípios RED/USE:

**HTTP (RED)**
- `requests_total` (por endpoint e status)
- `request_duration_ms` (histograma)
- `errors_total` (por `error.code` quando aplicável)

**Recursos (USE)**
- Conexões de DB em uso (se disponível via driver/pool)
- Tempo de query (se instrumentado)
- Filas internas / jobs (se houver posteriormente)

**Health endpoints**
- `GET /health`: liveness (retorna OK se processo está no ar)
- `GET /ready`: readiness (inclui checagem de dependências essenciais, ex: DB)

### 5) Tracing (preparo para distribuído)

- Adotar instrumentação compatível com **OpenTelemetry** para:
  - traces de requests HTTP
  - spans de chamadas ao banco (quando possível)
- Propagar contexto via headers quando aplicável (padrões OTel).
- Em ambiente inicial (MVP/desafio), tracing pode ser:
  - habilitado em staging
  - amostragem configurável em produção (ex: baixa taxa por padrão)

### 6) LGPD e segurança em observabilidade

- Proibir logar dados sensíveis e PII em texto claro, especialmente:
  - senhas, tokens, refresh tokens
  - documentos pessoais, endereço, telefone, e-mail
- Sanitização:
  - mascarar/truncar campos sensíveis quando inevitável
  - não logar corpo de request/response por padrão
- Retenção:
  - logs e traces com janela de retenção curta e controlada (configurável por ambiente)
- Acesso:
  - restringir acesso a dashboards/logs apenas a pessoas autorizadas

### 7) Configuração por ambiente

- Variáveis sugeridas:
  - `LOG_LEVEL` (default: INFO)
  - `LOG_FORMAT` (default: JSON)
  - `OTEL_ENABLED` (default: false)
  - `OTEL_SAMPLING_RATIO` (default: 0.01 em prod, configurável)
  - `METRICS_ENABLED` (default: true)
- Em `dev`:
  - logs podem ser human-readable opcionalmente, mas manter JSON como padrão para consistência.

---

## Rationale

- **Time pequeno:** logs estruturados e `request_id` reduzem drasticamente o tempo de diagnóstico.
- **Escala:** métricas de latência/erros permitem antecipar saturação (picos, endpoints problemáticos).
- **Múltiplos clientes:** facilita rastrear problemas específicos por rota e comportamento de consumo.
- **Evolução:** tracing preparado evita reescrita quando integrações crescerem.
- **LGPD:** evita vazamento de PII e reduz superfície de risco operacional.

---

## Consequences

### Positivas
- Troubleshooting mais rápido (correlação entre erro no cliente e logs do servidor).
- Monitoramento de performance e estabilidade com baixo overhead.
- Base pronta para evolução (APM/Tracing) sem reestruturar arquitetura.

### Negativas / Trade-offs
- Esforço inicial para padronizar middleware de request logging e correlation ID.
- Requer disciplina para não inserir logs com dados sensíveis.
- Instrumentação (tracing/métricas) pode adicionar overhead, mitigado por amostragem e configuração por ambiente.

---

## Implementation Notes (orientações)

- Implementar middleware para:
  - gerar/propagar `request_id`
  - medir tempo de request
  - registrar log de request final
  - incluir `X-Request-Id` na resposta
- Centralizar mapeamento de exceções para:
  - `error.code` estável
  - logar erro com `request_id` sem stacktrace exposta ao cliente
- Instrumentar DB (quando possível) com medição de tempo de query em logs DEBUG ou spans.

---

## Examples

### 1) Log de request (INFO)

```json
{
  "timestamp": "2026-01-27T23:10:12.345Z",
  "level": "INFO",
  "service": "offers-api",
  "env": "prod",
  "request_id": "req_01HXYZ...",
  "http.method": "GET",
  "http.path": "/api/v1/offers",
  "http.status_code": 200,
  "duration_ms": 37,
  "message": "request_completed"
}
````

### 2) Log de erro (ERROR)

```json
{
  "timestamp": "2026-01-27T23:10:14.012Z",
  "level": "ERROR",
  "service": "offers-api",
  "env": "prod",
  "request_id": "req_01HXYZ...",
  "error.code": "APPLICATION_ALREADY_EXISTS",
  "message": "business_rule_violation"
}
```

--- 

| **Anterior** |
|---------------|
| [ADR-008: Convenções de API](./10_adr_008_api_conventions.md) |