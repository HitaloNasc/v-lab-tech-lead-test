# ADR-005: Estratégia de Versionamento de API — URL-based (/api/v1)

**Status:** Aceito  
**Data:** 26/01/2026  
**Contexto:** A API será consumida por múltiplos clientes (web, mobile e integrações) e está sujeita a **mudanças frequentes de requisitos**. É necessário garantir **evolução controlada**, **compatibilidade retroativa** e **clareza operacional** para um time de backend pequeno, evitando que mudanças quebrem clientes existentes.

---

## Decisão

Adotar **versionamento de API baseado em URL**, no formato:

```
/api/v1/...
```


Cada versão principal (`v1`, `v2`, ...) representará um **contrato estável** e independente.

---

## Racional

- **Clareza explícita do contrato:**  
  A versão fica visível na URL, deixando claro para clientes e para o time qual contrato está sendo consumido.

- **Compatibilidade e evolução segura:**  
  Mudanças incompatíveis podem ser introduzidas em uma nova versão (`/v2`) sem impactar clientes que permanecem em `/v1`.

- **Simplicidade operacional:**  
  Versionamento por URL é simples de implementar, testar, documentar e depurar, reduzindo custo cognitivo para um time pequeno.

- **Observabilidade e auditoria:**  
  Logs, métricas e auditorias (LGPD logging) podem ser facilmente segmentados por versão, facilitando diagnóstico e análise de impacto.

- **Aderência a práticas comuns de mercado:**  
  O padrão `/api/v1` é amplamente adotado, bem compreendido por consumidores de API e compatível com ferramentas de documentação (OpenAPI).

---

## Consequências

### Positivas
- Evolução controlada da API sem quebra imediata de clientes.
- Contratos claros e previsíveis.
- Facilidade de manutenção e suporte a múltiplas versões em paralelo.
- Melhor rastreabilidade em logs e métricas por versão.

### Negativas / Trade-offs
- Necessidade de manter múltiplas versões ativas por um período (custo de manutenção).
- Possível duplicação de código entre versões se não houver estratégia de reaproveitamento.
- Requer governança para descontinuação (deprecation) de versões antigas.

---

## Diretrizes de Implementação

- **Formato de URL**
  - Todas as rotas devem ser prefixadas com a versão: `/api/v1/...`.

- **Critério para nova versão**
  - Criar nova versão **apenas** quando houver mudanças incompatíveis (breaking changes), como:
    - alteração de contratos de request/response,
    - mudança semântica de comportamento,
    - remoção de campos ou endpoints.

- **Mudanças compatíveis**
  - Adição de novos endpoints ou campos opcionais **não exige** nova versão.

- **Governança**
  - Documentar mudanças por versão (changelog).
  - Definir política de depreciação para versões antigas, com comunicação prévia aos consumidores.

- **Documentação**
  - Manter documentação OpenAPI separada por versão (ex.: `/docs/v1`).

---

## Alternativas Consideradas

1. **Versionamento via Header (ex.: `Accept-Version`)**
   - **Prós:** URLs mais limpas.  
   - **Contras:** menos visível, mais difícil de debugar e documentar; maior complexidade para clientes.

2. **Sem versionamento explícito**
   - **Prós:** simplicidade inicial.  
   - **Contras:** alto risco de quebra de clientes e evolução descontrolada.

3. **Versionamento por parâmetro de query**
   - **Prós:** implementação simples.  
   - **Contras:** padrão pouco adotado e semântica menos clara.

---

## Conclusão

O **versionamento por URL (`/api/v1`)** oferece o melhor equilíbrio entre **clareza**, **simplicidade**, **segurança evolutiva** e **baixo custo operacional**, sendo a estratégia mais adequada ao contexto do desafio e às necessidades de longo prazo da plataforma.

---

| **Anterior** | **Próximo** |
|---|---|
| [ADR-004: Padrão de API](./6_adr_004_api.md) | [ADR-006: LGPD Logging e Auditoria](./8_adr_006_lgpd.md) |