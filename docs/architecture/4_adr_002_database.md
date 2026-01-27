# ADR-002: Escolha do Banco de Dados - Por que PostgreSQL?

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A plataforma gerencia ofertas acadêmicas, candidaturas e dados pessoais, sendo consumida por múltiplos clientes. O desafio impõe **LGPD compliance**, **relacionamentos complexos**, **regras de unicidade**, **validações transacionais** e **escala para 100K+ usuários simultâneos**, além de exigir código manutenível por um time pequeno.

---

## Decisão

Adotar **PostgreSQL** como banco de dados relacional principal, utilizando um ORM (ex.: SQLAlchemy) e migrações versionadas (ex.: Alembic).

---

## Racional

- **Consistência e Integridade (ACID):**  
  Operações críticas (criação de candidatura, mudança de status, regras de unicidade) exigem transações confiáveis e integridade referencial forte.

- **Relacionamentos Complexos:**  
  O domínio possui múltiplas relações (Institution → Program/Offer; User ↔ Role; CandidateProfile → Application), que são naturalmente modeladas em SQL com FKs, constraints e joins eficientes.

- **LGPD e Auditoria:**  
  PostgreSQL oferece excelente suporte a:
  - **JSONB** (para `before/after` em auditoria),
  - **Índices** (inclusive parciais) para rastreabilidade,
  - **Transações** para garantir atomicidade entre ação de negócio e registro de auditoria.

- **Consultas com Filtros e Paginação:**  
  Listagens com filtros por instituição, tipo e status se beneficiam de índices compostos e planejamento de consultas maduros.

- **Maturidade e Ecossistema:**  
  Ferramentas consolidadas (ORMs, migrações, observabilidade) reduzem risco operacional e custo cognitivo para um time pequeno.

- **Escalabilidade Prática:**  
  Atende bem a cargas elevadas com:
  - leitura otimizada por índices,
  - paginação obrigatória,
  - possibilidade de réplicas de leitura no futuro.

---

## Consequências

### Positivas
- Forte garantia de integridade e previsibilidade de dados.
- Modelagem clara das regras de negócio diretamente no schema (constraints).
- Base sólida para auditoria e compliance (LGPD).
- Facilidade de manutenção e evolução com ferramentas maduras.

### Negativas / Trade-offs
- **Menor flexibilidade** para esquemas altamente dinâmicos em comparação a NoSQL.
- **Curva de aprendizado** em SQL e tuning de índices.
- Evoluções de schema requerem **migrações** (custo operacional adicional).

---

## Diretrizes de Implementação

- Utilizar **ORM** para produtividade, mantendo **constraints no banco** (unicidade, FKs, checks).
- Definir **índices** para:
  - filtros frequentes (institution, type, status),
  - unicidade de candidatura `(candidate_profile_id, offer_id)`,
  - auditoria (`entity_type`, `entity_id`, `occurred_at`).
- Usar **transações** para operações que combinam regra de negócio + auditoria.
- Manter **soft delete** para entidades de domínio, preservando histórico.
- Planejar **retenção** de logs de auditoria conforme políticas (sem hard delete imediato).

---

## Alternativas Consideradas

1. **NoSQL (ex.: MongoDB)**  
   - **Prós:** flexibilidade de schema, rapidez inicial.  
   - **Contras:** maior complexidade para garantir integridade, unicidade e transações; auditoria e joins mais custosos.

2. **Banco Relacional Diferente (ex.: MySQL)**  
   - **Prós:** similar em conceitos.  
   - **Contras:** recursos e ergonomia inferiores para JSON/índices avançados e ecossistema de observabilidade/auditoria no contexto proposto.

---

## Conclusão

PostgreSQL equilibra **consistência**, **auditabilidade**, **performance** e **maturidade**, atendendo aos requisitos funcionais e não funcionais do desafio, especialmente **LGPD logging** e **regras transacionais**, com menor risco e maior previsibilidade para a evolução do sistema.

---

| **Anterior** | **Próximo** |
|---|---|
| [ADR-001: Separação de Camadas](./3_adr_001_layers.md) | [ADR-003: Autenticação e Autorização](./5_adr_003_auth.md) |