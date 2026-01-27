# ADR-001: Separação de Camadas (Presentation / Application / Domain / Infrastructure)

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** Plataforma de gestão de ofertas acadêmicas e candidaturas, consumida por múltiplos clientes (web, mobile, integrações), com mudanças frequentes de requisitos, time de backend pequeno (2–3 pessoas) e necessidade de qualidade (testes, LGPD, escalabilidade). O desafio solicita uma arquitetura em camadas e justifica a separação para evolução futura.

---

## Decisão

Adotar uma arquitetura em camadas, separando explicitamente:

1. **Presentation Layer** (API REST / Controllers / Routers)  
2. **Application Layer** (Use Cases / Orquestração de regras)  
3. **Domain Layer** (Entidades, Value Objects, regras puras/invariantes)  
4. **Infrastructure Layer** (Persistência, repositórios, integrações e serviços técnicos)

A **Application Layer** será implementada entre a camada de API (Presentation) e o Domínio (Domain), sendo responsável por coordenar casos de uso, transações e validações dependentes de persistência.

---

## Racional

- **Testabilidade:** regras de negócio e validações (ex.: unicidade de candidatura, validação de deadline, RBAC) podem ser testadas em **unit tests** sem depender de HTTP, ORM ou banco.  
- **Baixo acoplamento:** mudanças em framework (FastAPI/Flask), formato HTTP ou detalhes de persistência (SQLAlchemy/PostgreSQL) não “vazam” para o domínio.  
- **Evolução com requisitos instáveis:** novas regras e fluxos entram como **novos casos de uso** sem exigir reestruturação de controllers ou entidades.  
- **Manutenibilidade em time pequeno:** responsabilidades ficam claras; o código tende a ser mais autoexplicativo e fácil de dar manutenção.  
- **LGPD e rastreabilidade:** auditoria e logging (ex.: `AuditEvent`, `DataAccessLog`) podem ser integrados na **Application Layer**, centralizando “efeitos colaterais” e evitando espalhar preocupações transversais em controllers ou entidades.

---

## Consequências

### Positivas
- Melhor isolamento e clareza de responsabilidades.
- Maior cobertura e qualidade de testes (unit/integration) com menos esforço.
- Facilidade para trocar/adicionar interfaces (ex.: integrações, novos clientes) mantendo o domínio estável.
- Caminho mais limpo para observabilidade e compliance (LGPD logging) sem poluir o domínio.

### Negativas / Trade-offs
- **Custo inicial** de organização (pastas, contratos, interfaces de repositório).
- Mais “boilerplate” (DTOs/schemas, mapeamentos, interfaces) do que uma abordagem monolítica simples.
- Exige disciplina para evitar “vazamento” de detalhes de infraestrutura para o domínio.

---

## Diretrizes de Implementação

- **Presentation Layer**
  - Apenas parsing/validação de entrada (Pydantic), autenticação/guards e mapeamento de erros HTTP.
  - Não conter regras de negócio.

- **Application Layer**
  - Implementar casos de uso (ex.: `CreateOffer`, `ListOffers`, `CreateApplication`, `UpdateApplicationStatus`).
  - Aplicar validações dependentes de dados (unicidade, deadline, RBAC).
  - Registrar auditoria e logs de acesso quando aplicável.
  - Coordenar transações (quando necessário).

- **Domain Layer**
  - Entidades e invariantes (ex.: `Offer` deve manter `application_deadline > publication_date`).
  - Regras puras e enums/VOs (sem dependências de framework ou banco).

- **Infrastructure Layer**
  - Repositórios concretos (SQLAlchemy), migrations (Alembic), providers técnicos (JWT, hashing), configurações e integrações.

---

## Alternativas Consideradas

1. **Arquitetura em 2 camadas (Controller + ORM/Models)**  
   - Mais simples no curto prazo, porém acopla negócio a HTTP/ORM, dificulta testes e evoluções frequentes.

2. **Arquitetura em 3 camadas (API / Services / Persistence) sem Domain explícito**  
   - Reduz boilerplate, mas tende a virar “service god object” e mistura regras com detalhes de persistência.

---

## Referências

- Desafio técnico V-LAB — seção de “Arquitetura de Camadas” e “ADRs” (modelo ADR-001).
