# ADR-003: Autenticação e Autorização — JWT + RBAC

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A plataforma é consumida por múltiplos clientes (web, mobile e integrações), possui endpoints públicos e protegidos, lida com **dados sensíveis** (LGPD) e precisa **escalar horizontalmente** para 100K+ usuários simultâneos. O desafio solicita justificar a escolha entre JWT, OAuth 2.0 e estratégias de autorização.

---

## Decisão

Adotar **JWT (JSON Web Token)** para autenticação **stateless** e **RBAC (Role-Based Access Control)** para autorização, com papéis persistidos em banco (`Role` + `UserRole`).

- Autenticação: **JWT assinado**, com expiração e validação em cada request.
- Autorização: **RBAC**, verificando papéis do usuário (ex.: `admin`, `user/candidate`) nos casos de uso e/ou guards da API.

---

## Racional

- **Stateless e Escalável:**  
  JWT elimina dependência de sessão em memória/estado compartilhado, facilitando escala horizontal e balanceamento de carga.

- **Simplicidade para Múltiplos Clientes:**  
  JWT é amplamente suportado por web e mobile, com fluxo simples (login → token → Authorization header).

- **Integração com RBAC:**  
  Papéis persistidos permitem regras claras como *“apenas admin pode criar offers”* sem acoplamento a endpoints específicos.

- **Segurança e LGPD:**  
  Tokens carregam apenas **claims mínimos** (ex.: `sub`, `roles`, `exp`), evitando exposição de dados pessoais. Controle de acesso centralizado reduz risco de acesso indevido.

- **Aderência ao Escopo do Desafio:**  
  OAuth 2.0 completo (authorization server, flows) adicionaria complexidade desnecessária para o cenário proposto, sem ganho proporcional.

---

## Consequências

### Positivas
- Autenticação simples e performática.
- Fácil integração com diferentes clientes.
- Autorização clara e extensível (novos papéis sem refatoração estrutural).
- Boa base para auditoria (actor_user_id nos logs).

### Negativas / Trade-offs
- Revogação imediata de tokens é limitada (exige estratégia adicional).
- Exige cuidado com:
  - tempo de expiração,
  - armazenamento seguro do token no cliente,
  - rotação de chaves (se aplicável).
- RBAC puro pode ser insuficiente para regras muito granulares (ABAC), exigindo extensão futura.

---

## Diretrizes de Implementação

- **JWT**
  - Assinatura com segredo forte (ou chave assimétrica, se necessário).
  - Claims mínimos: `sub` (user_id), `roles`, `exp`.
  - Expiração curta com renovação controlada (quando aplicável).

- **RBAC**
  - Papéis persistidos (`Role`, `UserRole`).
  - Verificação de autorização em guards/decorators **e** reforço nos casos de uso críticos.
  - Exemplo: criação de `Offer` restrita a usuários com role `admin`.

- **Segurança**
  - Hash de senha com algoritmo forte (ex.: bcrypt).
  - Proteção de endpoints com middleware/guard `@require_auth`.
  - CORS configurado corretamente.
  - Rate limiting básico por IP para endpoints sensíveis (login).

- **Auditoria**
  - `actor_user_id` derivado do JWT para registrar ações em `AuditEvent`.
  - Acessos a dados pessoais registrados em `DataAccessLog` quando aplicável.

---

## Alternativas Consideradas

1. **OAuth 2.0 completo (Authorization Server)**  
   - **Prós:** padrão robusto para ecossistemas complexos.  
   - **Contras:** alto custo de implementação e operação; escopo além do necessário para o desafio.

2. **Sessões server-side (cookies/sessions)**  
   - **Prós:** revogação imediata.  
   - **Contras:** dificulta escala horizontal e integração com clientes móveis.

3. **ABAC (Attribute-Based Access Control)**  
   - **Prós:** autorização mais granular.  
   - **Contras:** maior complexidade; não justificada no escopo atual.

---

## Conclusão

A combinação **JWT + RBAC** oferece o melhor equilíbrio entre **segurança**, **simplicidade**, **escalabilidade** e **aderência ao escopo** do desafio, atendendo aos requisitos funcionais e não funcionais (LGPD, performance e manutenibilidade) com menor risco e maior previsibilidade de evolução.

---

<div style="display: flex; justify-content: space-between; gap: 16px; margin-top: 24px;">

  <!-- Anterior -->
  <a href="./4_adr_002_database.md"
     style="
       flex: 1;
       padding: 12px 16px;
       border: 1px solid #d0d7de;
       border-radius: 6px;
       text-decoration: none;
       color: inherit;
       text-align: right;
     ">
    ADR-002: Escolha do Banco de Dados
  </a>

  <!-- Próximo -->
  <a href="./6_adr_004_api.md"
     style="
       flex: 1;
       padding: 12px 16px;
       border: 1px solid #d0d7de;
       border-radius: 6px;
       text-decoration: none;
       color: inherit;
       text-align: right;
     ">
    ADR-004: Padrão de API
  </a>

</div>