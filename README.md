# v-lab-api

Backend desenvolvido em **FastAPI** para gerenciamento de **ofertas acadêmicas** (cursos, bolsas, vagas), **instituições**, **programas**, **candidatos** e **candidaturas**, como parte do desafio técnico para a vaga de **Líder Técnico em Desenvolvimento** do V-LAB.

A API foi projetada para ser consumida por múltiplos clientes (web, mobile e integrações), com foco em **arquitetura limpa**, **segurança**, **escalabilidade** e **manutenibilidade**.

---

## 📚 Documentação

Toda a documentação técnica produzida durante o desafio está disponível na pasta:

👉 **[docs/architecture](./docs/architecture)**

Inclui, entre outros artefatos:
- Modelo de dados conceitual
- Levantamento de requisitos
- Design arquitetural
- Architecture Decision Records (ADRs)
- Decisões de segurança, versionamento e persistência

---

## 🚀 Funcionalidades Principais

- Autenticação e autorização via JWT
- Controle de acesso baseado em papéis (RBAC)
- Administração institucional:
  - Usuários `institution_admin` vinculados a uma `Institution`
  - Operações restritas ao contexto institucional do usuário
- CRUD de entidades centrais:
  - Ofertas acadêmicas (cursos, bolsas, estágios)
  - Instituições
  - Programas institucionais
  - Candidaturas
- Fluxo de candidaturas com regras de negócio:
  - Unicidade de candidatura por oferta
  - Validação de prazo de inscrição
  - Alteração de status restrita a admins institucionais
- Separação entre identidade e dados pessoais (privacy-by-design):
  - `User` para autenticação/autorização
  - `CandidateProfile` para dados do candidato
- API REST versionada (`/api/v1`)
- Documentação OpenAPI automática (Swagger UI)

---

## 🧩 Arquitetura

A aplicação segue uma arquitetura em camadas inspirada em **Clean Architecture / Hexagonal**, separando responsabilidades entre:

- **Presentation Layer** — Controllers / API REST
- **Application Layer** — Casos de uso
- **Domain Layer** — Entidades e regras de negócio
- **Infrastructure Layer** — Banco de dados, ORM, serviços externos

As decisões arquiteturais estão documentadas em **ADRs** dentro da pasta `docs/architecture`.

---

## 📖 API Docs (Swagger)

A API expõe documentação interativa via Swagger UI:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Visão geral dos endpoints

![Swagger UI](swagger-ui.jpeg)

---

## ⚙️ Requisitos

- Python **3.10+**
- pip
- Docker & docker-compose (opcional, recomendado para banco)
- Make

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com, no mínimo:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vlab
JWT_SECRET_KEY=your-secret-key
```

O projeto utiliza pydantic-settings para carregamento automático das variáveis.

> 💡 Veja .env.example para referência.


## 🛠️ Setup local (sem Docker)

- Criar virtualenv:

```bash
make venv
```

- Instalar dependências:

```bash
make install
```

- Rodar migrações (executar o banco antes — ver seção Docker abaixo):

```bash
make migrate
```

- Rodar a aplicação:

```bash
make run
```

A API ficará disponível em [http://localhost:8000](http://localhost:8000)

## 🐳 Setup com Docker

- Subir somente o banco:

```bash
make db-up
```

- Subir a aplicação em Docker (build + up):

```bash
make docker-build
make run-docker
```

## 📌 Notas Técnicas

- Configurações centrais em: app/config/settings.py
- Entry point da aplicação: app.main:app
- Migrations gerenciadas com Alembic
- Banco de dados: PostgreSQL

## Comandos úteis

- `make test` — roda os testes
- `make coverage` — testes com relatório de cobertura
- `make lint` — ruff + mypy
- `make format` — black
- `make clean` — limpa caches

## 📋 Checklist do Desafio Técnico

### Arquitetura & Design
- [x] Arquitetura em camadas documentada
- [x] Modelo de dados conceitual
- [x] ADRs documentados
- [x] Versionamento de API (`/api/v1`)
- [x] Padrão de tratamento de erros

### Segurança
- [x] Registro de usuário
- [x] Hash de senha (bcrypt)
- [x] Login com JWT
- [x] Proteção de endpoints
- [x] Autorização baseada em roles (RBAC)

### Funcionalidades
- [x] CRUD de ofertas
- [x] CRUD de instituições
- [x] CRUD de programas
- [x] CRUD de candidaturas
- [x] Validação de duplicidade de candidatura
- [x] Validação de datas e deadlines

### Qualidade & Infra
- [x] Migrations com Alembic
- [x] Docker Compose para banco
- [ ] Testes automatizados *(documentado, não implementado)*
- [x] Documentação OpenAPI
- [x] README completo

### LGPD & Governança de Dados
- [ ] Consentimento contextual por candidatura *(documentado no design)*
- [ ] Auditoria de alterações (AuditEvent) *(documentado no design)*
- [ ] Log de acesso a dados pessoais (DataAccessLog) *(documentado no design)*

## ⚖️ Decisões de Escopo e Trade-offs

Devido à limitação de tempo do desafio, algumas funcionalidades importantes foram **deliberadamente documentadas no design, mas não implementadas** nesta entrega inicial.

### Testes Automatizados
A estratégia de testes (unitários e de integração) foi definida, porém sua implementação foi despriorizada para priorizar:
- modelagem correta do domínio;
- definição clara das regras de negócio;
- estrutura arquitetural extensível e bem documentada.

O projeto está preparado para receber testes com `pytest` e `pytest-cov` sem necessidade de refatorações estruturais.

### LGPD: Consentimento e Auditoria
Os mecanismos de:
- consentimento contextual por candidatura;
- auditoria de alterações (AuditEvent);
- log de acesso a dados pessoais (DataAccessLog);

foram **explicitamente modelados e documentados** na arquitetura e nos ADRs, mas não implementados nesta versão por:
- exigirem maior esforço de persistência, observabilidade e validações transversais;
- não serem críticos para validação do fluxo funcional principal no tempo do desafio.

A decisão foi priorizar um **core funcional sólido**, com regras de acesso bem definidas (RBAC + vínculo institucional), deixando os mecanismos de governança de dados prontos para evolução incremental.

Essas decisões seguem o princípio de **entrega incremental com segurança de evolução**, comum em ambientes de produto e times pequenos.

## 📄 Licença
Projeto desenvolvido exclusivamente para fins de avaliação técnica.