.PHONY: help build up down logs clean shell-backend test test-backend test-frontend

# ==============================================================================
# Main Commands
# ==============================================================================

help:
	@echo "FlowGuard-Engine - Makefile"
	@echo "=============================================="
	@echo "make build        : Rebuild all containers (no-cache)"
	@echo "make up           : Start the system (detached)"
	@echo "make down         : Stop the system"
	@echo "make logs         : View live logs (Ctrl+C to exit)"
	@echo "make clean        : Stop system + remove volumes & pycache"
	@echo "make shell-backend: Open Bash shell inside Backend container"
	@echo "make test         : Run ALL tests (Backend + Frontend)"
	@echo "make test-backend : Run Backend tests with Coverage"
	@echo "make test-frontend: Run Frontend tests (Vitest)"

# Force rebuild to ensure dependencies are fresh
build:
	docker-compose build --no-cache
	docker-compose up -d
	@echo "System Rebuilt."
	@echo "  - Frontend: http://localhost:5173/"
	@echo "  - Backend:  http://localhost:8000/docs"
	@echo "  - Qdrant:   http://localhost:6333/dashboard"

up:
	docker-compose up -d
	@echo "System running at:"
	@echo "  - Frontend: http://localhost:5173/"
	@echo "  - Backend:  http://localhost:8000/docs"
	@echo "  - Qdrant:   http://localhost:6333/dashboard"

down:
	docker-compose down

logs:
	docker-compose logs -f

# ==============================================================================
# Development Helpers
# ==============================================================================

shell-backend:
	docker-compose exec backend /bin/bash

# Nuclear cleanup option
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleaning Python bytecode and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "Clean complete."

# ==============================================================================
# Testing Strategy
# ==============================================================================

test: test-backend test-frontend

# FIX APPLIED: Added '-e PYTHONPATH=/app' so pytest can resolve 'src'
test-backend:
	@echo "---------------------------------------"
	@echo "Running BACKEND tests (Pytest + Coverage)"
	@echo "---------------------------------------"
	docker-compose exec -e PYTHONPATH=/app backend pytest --cov=src tests/ -v

# Executes tests inside the running Frontend Dev container
test-frontend:
	@echo "---------------------------------------"
	@echo "Running FRONTEND tests (Vitest)"
	@echo "---------------------------------------"
	docker-compose exec frontend npm test