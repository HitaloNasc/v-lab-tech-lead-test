reset-db:
	docker-compose down -v
	docker-compose up -d db
	sleep 3
	docker-compose run --rm api alembic upgrade head
.PHONY: help run run-docker test coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  make run        - Run the API locally"
	@echo "  make run-docker - Run the API in Docker"
	@echo "  make test       - Run tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make lint       - Run linters and type checks"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean cache files"

run:
	uvicorn app.main:app --reload

run-docker:
	docker-compose up --build

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
