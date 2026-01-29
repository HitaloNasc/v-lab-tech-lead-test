# v-lab-api

Projeto backend FastAPI para gerenciamento de ofertas acadêmicas.
![alt text](swagger-ui.jpeg)

## Requisitos

- Python 3.10+ (recomendado)
- pip
- Docker & docker-compose (opcional, recomendado para banco)

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com pelo menos as seguintes variáveis:

- `DATABASE_URL` (ex.: postgres://user:pass@localhost:5432/dbname)
- `JWT_SECRET_KEY`

O projeto usa `pydantic-settings` e carrega `.env` automaticamente.

## Setup local (sem Docker)

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

A API ficará disponível em http://localhost:8000

## Setup com Docker

- Subir somente o banco:

```bash
make db-up
```

- Subir a aplicação em Docker (build + up):

```bash
make docker-build
make run-docker
```

Com Docker, as migrations podem ser executadas apontando para o container do app ou via `make migrate` se usar `.venv` local.

## OpenAPI / Docs

- Documentação interativa (Swagger UI): http://localhost:8000/docs

## Comandos úteis

- `make test` — roda os testes
- `make coverage` — testes com relatório de cobertura
- `make lint` — ruff + mypy
- `make format` — black
- `make clean` — limpa caches

## Notas

- As configurações obrigatórias estão em [app/config/settings.py](app/config/settings.py).
- O ponto de entrada da aplicação é `app.main:app` (usado pelo `uvicorn`).

Se quiser, posso também adicionar um arquivo `.env.example` com valores de exemplo.
# Como rodar o projeto FastAPI

1. Ative o ambiente virtual:
   
   source .venv/bin/activate

2. Instale as dependências (se necessário):
   
   pip install -r requirements.txt

3. Execute o servidor:
   
   uvicorn src.main:app --reload

4. Acesse http://127.0.0.1:8000/ no navegador.

5. Para verificar o endpoint de saúde:
   
   http://127.0.0.1:8000/health

6. Para documentação automática:
   
   http://127.0.0.1:8000/docs
