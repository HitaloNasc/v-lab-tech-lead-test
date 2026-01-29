help:
	@echo "Available commands:"
	@echo "  make venv         - Create Python virtualenv (.venv)"
	@echo "  make install      - Install dependencies into .venv"
	@echo "  make install-dev  - Install dev dependencies into .venv"
	@echo "  make db-up        - Start just the database (docker-compose)"
	@echo "  make migrate      - Run alembic migrations (upgrade head)"
	@echo "  make run          - Run the API locally (uses .venv if present)"
	@echo "  make run-docker   - Run the API in Docker"
	@echo "  make docker-build - Build docker images"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make lint         - Run linters and type checks"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache files"

run:
	if [ -d .venv ]; then . .venv/bin/activate; fi && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-docker:
	docker-compose up --build

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

install-dev:
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt

db-up:
	docker-compose up -d db

migrate:
	. .venv/bin/activate && alembic upgrade head

migrate-autogen:
	. .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

docker-build:
	docker-compose build

test:
	pytest

coverage:
	pytest --cov=app --cov-report=html

lint:
	ruff check .
	mypy .

format:
	black .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov

reset-db:
	docker-compose down -v
	docker-compose up -d db
	sleep 3
	docker-compose run --rm api alembic upgrade head
.PHONY: help run run-docker test coverage lint format clean

