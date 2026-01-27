# ADR-004: Padrão de API — REST API Versionada

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A plataforma expõe funcionalidades de gestão de ofertas acadêmicas e candidaturas para múltiplos clientes (web, mobile e integrações). O desafio solicita justificar a escolha do padrão de design de API (RESTful puro vs. GraphQL) e definir uma estratégia que favoreça simplicidade, escalabilidade, manutenibilidade e evolução do sistema.

---

## Decisão

Adotar **API RESTful**, com recursos bem definidos e **versionamento via URL** (`/api/v1/...`), utilizando HTTP methods e status codes padrão.

---

## Racional

- **Aderência ao domínio do problema:**  
  O escopo do sistema é fortemente orientado a **CRUD** e fluxos previsíveis (Offers, Applications, Users), que se encaixam naturalmente no modelo REST (recursos + verbos HTTP).

- **Simplicidade e clareza:**  
  REST é amplamente conhecido, reduz curva de aprendizado e facilita manutenção por um time pequeno (2–3 pessoas).

- **Compatibilidade com múltiplos clientes:**  
  Web, mobile e integrações de terceiros consomem REST de forma simples e consistente, sem necessidade de tooling específico.

- **Observabilidade e Debug:**  
  REST facilita:
  - uso direto de HTTP status codes,
  - logging por endpoint,
  - auditoria de ações (mapeamento claro entre request e recurso afetado).

- **Evolução controlada:**  
  O versionamento por URL permite introduzir mudanças incompatíveis sem quebrar clientes existentes.

- **Escopo do desafio:**  
  GraphQL introduziria complexidade adicional (schema, resolvers, caching, autorização por campo) sem benefício claro para o volume e tipo de operações requeridas.

---

## Consequências

### Positivas
- API simples, previsível e fácil de documentar.
- Melhor alinhamento com práticas padrão de mercado.
- Facilidade de testes (unitários e de integração).
- Integração direta com ferramentas de observabilidade e segurança.

### Negativas / Trade-offs
- Overfetching ou underfetching em alguns cenários (menos flexível que GraphQL).
- Evolução de payloads exige versionamento ou cuidado com compatibilidade.
- Menor flexibilidade para consultas altamente customizadas.

---

## Diretrizes de Implementação

- **Recursos REST**
  - `/api/v1/offers`
  - `/api/v1/applications`
  - `/api/v1/users`
  - `/api/v1/auth/*`

- **Verbos HTTP**
  - `POST` para criação
  - `GET` para leitura
  - `PUT` para atualização
  - `DELETE` para remoção lógica (soft delete)

- **Status Codes**
  - `200 OK`, `201 Created`
  - `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`
  - `404 Not Found`, `409 Conflict`
  - `422 Unprocessable Entity`

- **Paginação**
  - Obrigatória em listagens (`limit` + `offset`).

- **Documentação**
  - OpenAPI / Swagger gerado automaticamente a partir dos schemas.

---

## Alternativas Consideradas

1. **GraphQL**
   - **Prós:** flexibilidade de consultas, redução de overfetching.  
   - **Contras:** maior complexidade de implementação, caching e autorização; não necessário para o escopo atual.

2. **gRPC**
   - **Prós:** alta performance e contratos fortes.  
   - **Contras:** menos amigável para clientes web/mobile e integrações simples; custo operacional maior.

3. **REST sem versionamento explícito**
   - **Prós:** menos URLs.  
   - **Contras:** dificulta evolução e compatibilidade futura.

---

## Conclusão

Uma **API REST versionada** oferece o melhor equilíbrio entre **simplicidade**, **manutenibilidade**, **compatibilidade** e **evolução controlada**, atendendo plenamente às necessidades do desafio e ao perfil de um time pequeno responsável por um sistema em crescimento.

---

<div style="display: flex; justify-content: space-between; gap: 16px; margin-top: 24px;">

  <!-- Anterior -->
  <a href="./5_adr_003_auth.md"
     style="
       flex: 1;
       padding: 12px 16px;
       border: 1px solid #d0d7de;
       border-radius: 6px;
       text-decoration: none;
       color: inherit;
       text-align: right;
     ">
    ADR-003: Autenticação e Autorização
  </a>

  <!-- Próximo -->
  <a href="./7_adr_005_versioning.md"
     style="
       flex: 1;
       padding: 12px 16px;
       border: 1px solid #d0d7de;
       border-radius: 6px;
       text-decoration: none;
       color: inherit;
       text-align: right;
     ">
    ADR-005: Estratégia de Versionamento
  </a>

</div>