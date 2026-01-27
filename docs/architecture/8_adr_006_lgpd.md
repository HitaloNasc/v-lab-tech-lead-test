# ADR-006: LGPD Logging e Auditoria — AuditEvent e DataAccessLog

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A plataforma manipula **dados pessoais** de candidatos e informações sensíveis relacionadas a processos seletivos. O desafio explicita que **LGPD compliance é obrigatório** e menciona a necessidade de **LGPD logging**. Além disso, o sistema precisa permitir rastreabilidade de ações administrativas, investigações de incidentes e prestação de contas (accountability).

---

## Decisão

Adotar uma **estratégia explícita de logging e auditoria para LGPD**, composta por duas estruturas distintas e complementares:

1. **AuditEvent** — auditoria de **alterações** (write/audit trail)  
2. **DataAccessLog** — auditoria de **acessos/leitura** (read/access trail)

Ambas as tabelas serão **append-only**, com política de retenção definida, e integradas à Application Layer.

---

## Racional

- **Accountability (LGPD):**  
  A LGPD exige que o controlador seja capaz de **demonstrar** como dados pessoais são tratados. Isso inclui saber **quem alterou** e **quem acessou** dados pessoais.

- **Separação de responsabilidades:**  
  Alterações e acessos são eventos diferentes:
  - mudanças impactam integridade e estado do sistema,
  - acessos impactam privacidade.  
  Separar os dois tipos evita ambiguidade e simplifica auditorias.

- **Rastreabilidade técnica:**  
  Registrar `actor_user_id`, `request_id`, IP e user-agent permite correlacionar ações com:
  - logs da aplicação,
  - métricas,
  - investigações de incidentes.

- **Minimização de dados:**  
  O uso de `before/after` em JSONB permite registrar **apenas campos relevantes**, evitando persistir dados pessoais completos quando não necessário.

- **Centralização na Application Layer:**  
  A Application Layer é o ponto ideal para registrar auditoria, pois conhece:
  - o ator,
  - a regra de negócio aplicada,
  - o impacto da operação,
  sem acoplar essas preocupações ao domínio ou à camada HTTP.

---

## Consequências

### Positivas
- Conformidade prática com LGPD (accountability e rastreabilidade).
- Maior transparência sobre ações administrativas e acessos a dados pessoais.
- Base sólida para auditorias internas e externas.
- Facilita investigação de falhas, abusos ou incidentes de segurança.

### Negativas / Trade-offs
- Aumento no volume de dados armazenados (logs).
- Pequeno overhead de escrita em operações sensíveis.
- Necessidade de governança clara sobre retenção e acesso aos logs.
- Exige cuidado para não vazar dados sensíveis dentro dos próprios registros de auditoria.

---

## Diretrizes de Implementação

### AuditEvent (alterações)
- Registrar eventos para:
  - criação/atualização/remoção lógica de Offers,
  - criação e mudança de status de Applications,
  - atualização de CandidateProfile,
  - soft delete de User.
- Campos principais:
  - `occurred_at`, `actor_user_id`, `action`, `entity_type`, `entity_id`,
    `before`, `after`, `request_id`.
- **Append-only:** não permitir UPDATE ou DELETE.
- Registrar apenas campos alterados em `before/after`.

### DataAccessLog (acessos)
- Registrar acessos a dados pessoais, especialmente quando:
  - o ator não é o próprio titular,
  - o acesso é administrativo ou institucional.
- Campos principais:
  - `accessed_at`, `actor_user_id`, `data_subject_user_id`,
    `resource`, `resource_id`, `purpose`, `request_id`.
- Não registrar acessos a dados agregados ou anonimizados.

### Segurança e Governança
- Restringir acesso às tabelas de auditoria a perfis administrativos específicos.
- Definir política de **retenção** (ex.: 3–5 anos), evitando exclusão imediata.
- Evitar armazenar dados pessoais completos (CPF, e-mail) nos logs.

---

## Alternativas Consideradas

1. **Logging apenas em arquivos (logs de aplicação)**  
   - **Prós:** implementação simples.  
   - **Contras:** difícil consulta, baixa rastreabilidade, não atende LGPD de forma adequada.

2. **Auditoria apenas de alterações (sem log de acesso)**  
   - **Prós:** menor volume de dados.  
   - **Contras:** não cobre requisito essencial de saber quem visualizou dados pessoais.

3. **Triggers no banco para auditoria**  
   - **Prós:** captura automática de mudanças.  
   - **Contras:** menor contexto de negócio (ator, finalidade, request), maior acoplamento ao schema.

---

## Conclusão

A adoção explícita de **AuditEvent** e **DataAccessLog** fornece uma solução equilibrada para **LGPD logging**, atendendo requisitos legais, técnicos e operacionais. Essa estratégia garante **rastreabilidade**, **accountability** e **governança**, sem comprometer a manutenibilidade ou a evolução da arquitetura.
