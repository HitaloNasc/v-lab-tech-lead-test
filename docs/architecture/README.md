# Architecture Documentation

Este diretório contém a **documentação arquitetural** da plataforma de gestão de ofertas acadêmicas (cursos, bolsas e estágios).  
O objetivo é registrar, de forma clara e rastreável, as **principais decisões técnicas**, a **estrutura do sistema** e os **padrões adotados**, servindo como referência para desenvolvimento, evolução e avaliação técnica do projeto.

A documentação foi organizada seguindo boas práticas de **Architecture Decision Records (ADR)**, com foco em simplicidade, manutenibilidade e suporte à evolução contínua do sistema, considerando um time de backend reduzido e requisitos sujeitos a mudanças frequentes.

---

## 📌 Visão Geral do Conteúdo

- **Requisitos**: contexto do problema e necessidades funcionais e não funcionais.
- **Design Arquitetural**: visão geral da arquitetura e suas camadas.
- **ADRs**: decisões arquiteturais fundamentais, com racional e consequências.
- **Diagramas**: representações visuais para facilitar entendimento rápido do sistema.

---

## 📖 Ordem de Leitura Recomendada

1. **Requisitos**
   - [`1_requirements_capture.md`](./1_requirements_capture.md)

2. **Visão Geral do Design**
   - [`2_design.md`](./2_design.md)

3. **Decisões Arquiteturais (ADRs)**
   - [`3_adr_001_layers.md`](./3_adr_001_layers.md)
   - [`4_adr_002_database.md`](./4_adr_002_database.md)
   - [`5_adr_003_auth.md`](./5_adr_003_auth.md)
   - [`6_adr_004_api.md`](./6_adr_004_api.md)
   - [`7_adr_005_versioning.md`](./7_adr_005_versioning.md)
   - [`8_adr_006_lgpd.md`](./8_adr_006_lgpd.md)
   - [`9_adr_007_delete_strategy.md`](./9_adr_007_delete_strategy.md)
   - [`10_adr_008_api_conventions.md`](./10_adr_008_api_conventions.md)
   - [`11_adr_009_observability.md`](./11_adr_009_observability.md)

4. **Diagramas**
   - Modelo de dados conceitual
   - Arquitetura em camadas (simplificada)

---

## 🖼️ Diagramas

Os diagramas estão disponíveis em [`./diagrams`](./diagrams):

- **Modelo de Dados Conceitual**
  - `concept_data_model.png`
  - `concept_data_model.puml`
- **Arquitetura em Camadas (Simplificada)**
  - `layers_simple.png`
  - `layers_simple.puml`

Esses diagramas complementam a documentação textual e permitem uma compreensão visual rápida da estrutura do sistema.

---

## 🎯 Objetivo da Documentação

Esta documentação serve para:
- Apoiar decisões técnicas presentes e futuras
- Facilitar onboarding de novos desenvolvedores
- Reduzir ambiguidade arquitetural
- Demonstrar clareza e maturidade técnica no design do sistema
- Atender aos requisitos de documentação do desafio técnico

Qualquer mudança estrutural relevante no sistema **deve resultar em um novo ADR** ou na atualização de um existente, preservando o histórico de decisões.

---

| **Próximo** |
|---------------|
| [Captura de Requisitos](./1_requirements_capture.md) |