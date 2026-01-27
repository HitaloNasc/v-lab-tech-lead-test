# ADR-007: Estratégia de Exclusão de Dados — Soft Delete vs Hard Delete

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A plataforma gerencia dados pessoais (LGPD), histórico de candidaturas e decisões administrativas. Há necessidade de **preservar rastreabilidade**, **integridade referencial** e **accountability**, ao mesmo tempo em que se respeitam direitos do titular (ex.: exclusão/eliminação) e requisitos operacionais (auditoria e histórico).

---

## Decisão

Adotar **Soft Delete** como estratégia padrão para entidades de domínio, mantendo **Hard Delete** restrito a dados técnicos/temporários ou a processos controlados de **retenção/anonimização**.

- **Soft Delete**: marcar registros como removidos logicamente (`deleted_at`, e quando aplicável `deleted_by`, `deletion_reason`).
- **Hard Delete**: permitido apenas para dados técnicos (tokens expirados, buckets de rate limit, caches) ou após políticas formais de retenção/anonimização.

---

## Racional

- **LGPD e Accountability:**  
  Soft delete preserva histórico e trilhas de auditoria, permitindo demonstrar *quando* e *por quem* um registro foi removido logicamente, sem apagar evidências necessárias.

- **Integridade Referencial:**  
  Evita quebra de relações (ex.: candidaturas vinculadas a ofertas/usuários) e inconsistências em relatórios e auditorias.

- **Rastreabilidade Operacional:**  
  Mantém consistência com `AuditEvent` e `DataAccessLog`, permitindo reconstruir eventos e decisões passadas.

- **Evolução e Suporte:**  
  Facilita recuperação administrativa (undo lógico) e análise de incidentes, reduzindo risco operacional.

- **Separação de Preocupações:**  
  Direitos do titular (eliminação) podem ser atendidos por **anonimização** após prazos de retenção, em vez de exclusão física imediata.

---

## Consequências

### Positivas
- Preserva histórico e evidências legais.
- Mantém integridade e previsibilidade do domínio.
- Facilita auditoria, suporte e investigação de incidentes.
- Alinha-se a LGPD (accountability, minimização e governança).

### Negativas / Trade-offs
- Aumenta volume de dados armazenados.
- Exige disciplina para filtrar registros `deleted_at IS NULL` nas consultas.
- Requer políticas claras de retenção/anonimização para evitar acúmulo indefinido.

---

## Diretrizes de Implementação

### Entidades com **Soft Delete**
- `User`
- `CandidateProfile`
- `Institution`
- `Program`
- `Offer`
- `Application`

**Campos padrão:**
- `deleted_at` (timestamptz)
- `deleted_by` (quando aplicável)
- `deletion_reason` (opcional)

### Entidades **sem Soft Delete**
- `AuditEvent`
- `DataAccessLog`

> **Nota:** logs de auditoria são **append-only**; não atualizar nem deletar. Aplicar apenas políticas de retenção.

### Consultas e Índices
- Filtrar registros ativos com `deleted_at IS NULL`.
- Criar índices parciais quando necessário para performance.

### Retenção e Anonimização
- Definir política (ex.: 3–5 anos) para logs e dados históricos.
- Atender pedidos de eliminação por **anonimização** (ex.: remover/mascarar CPF, email), preservando chaves técnicas quando exigido por auditoria.

---

## Alternativas Consideradas

1. **Hard Delete por padrão**
   - **Prós:** menor volume de dados.
   - **Contras:** perda de histórico, quebra de integridade, risco legal (LGPD).

2. **Anonimização imediata em vez de Soft Delete**
   - **Prós:** forte foco em privacidade.
   - **Contras:** dificulta auditoria e suporte; perde contexto operacional.

3. **Exclusão via triggers automáticos**
   - **Prós:** automação.
   - **Contras:** menor controle de negócio e contexto; risco operacional.

---

## Conclusão

O **Soft Delete** como padrão, combinado com **políticas de retenção e anonimização**, oferece o melhor equilíbrio entre **conformidade LGPD**, **integridade do domínio**, **rastreabilidade** e **manutenibilidade**. O **Hard Delete** permanece restrito a dados técnicos ou a processos controlados, reduzindo riscos legais e operacionais.

---

| **Anterior** | **Próximo** |
|---|---|
| [ADR-006: LGPD Logging e Auditoria](./8_adr_006_lgpd.md)| [ADR-008: Convenções de API](./10_adr_008_api_conventions.md) |
