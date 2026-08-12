.PHONY: help up down build logs health test lint install-dev clean migrate seed

SHELL := /bin/bash
SERVICES := api-gateway transaction-service event-bus orchestration-engine connector-framework notification-service

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ─── Docker ───────────────────────────────────────────────────────────────────

up: ## Start all services (detached)
	docker compose up -d

up-infra: ## Start only infrastructure (postgres, redis, rabbitmq)
	docker compose up -d postgres redis rabbitmq

up-obs: ## Start observability stack
	docker compose up -d prometheus grafana jaeger

down: ## Stop all services
	docker compose down

down-volumes: ## Stop all services and remove volumes (DESTRUCTIVE)
	@read -p "This will delete all data volumes. Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ]; then docker compose down -v; else echo "Aborted."; fi

build: ## Build all service images
	docker compose build

build-%: ## Build a specific service: make build-api-gateway
	docker compose build $*

logs: ## Follow logs for all services
	docker compose logs -f

logs-%: ## Follow logs for a specific service: make logs-api-gateway
	docker compose logs -f $*

restart-%: ## Restart a specific service
	docker compose restart $*

ps: ## Show running containers
	docker compose ps

# ─── Health ───────────────────────────────────────────────────────────────────

health: ## Check health of all services
	@echo "Checking service health..."
	@for svc in $(SERVICES); do \
		port=$$(docker compose port $$svc 8000 2>/dev/null | cut -d: -f2); \
		echo "  $$svc -> http://localhost:$$port/health"; \
	done
	@python scripts/health_check.py

# ─── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all tests
	@for svc in $(SERVICES); do \
		echo "Testing $$svc..."; \
		cd services/$$svc && python -m pytest tests/ -v && cd ../..; \
	done

test-%: ## Test a specific service: make test-api-gateway
	cd services/$* && python -m pytest tests/ -v

# ─── Linting & Formatting ─────────────────────────────────────────────────────

lint: ## Lint all services with ruff
	ruff check services/ shared/

format: ## Format all code with ruff
	ruff format services/ shared/

typecheck: ## Run mypy type checking
	mypy services/ shared/ --ignore-missing-imports

# ─── Database ─────────────────────────────────────────────────────────────────

migrate: ## Run database migrations
	cd services/transaction-service && alembic upgrade head

migrate-down: ## Rollback last migration
	cd services/transaction-service && alembic downgrade -1

seed: ## Seed development data
	python scripts/seed_db.py

# ─── Dev Setup ────────────────────────────────────────────────────────────────

install-dev: ## Install dev tools globally (ruff, mypy, pytest)
	pip install ruff mypy pytest pytest-asyncio httpx

setup: ## Full local dev setup
	@echo "Copying .env.example -> .env"
	@cp -n .env.example .env || echo ".env already exists, skipping."
	@echo "Starting infrastructure..."
	@$(MAKE) up-infra
	@echo "Running migrations..."
	@sleep 5 && $(MAKE) migrate
	@echo "Seeding dev data..."
	@$(MAKE) seed
	@echo "Done. Run 'make up' to start all services."

clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
