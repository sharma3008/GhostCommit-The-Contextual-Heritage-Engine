.PHONY: up down logs test lint typecheck fmt

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f api

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff format .

typecheck:
	mypy app
