# ============================================================================
# Enterprise Text2SQL Engine - Automation Makefile (Port 8502)
# ============================================================================

.PHONY: help install init-db test test-unit test-e2e run run-cli docker-build docker-up docker-down clean

PYTHON := python3
PIP := pip
STREAMLIT := streamlit
PORT := 8502

help:
	@echo "Available commands:"
	@echo "  make install       Install all Python dependencies"
	@echo "  make init-db       Seed and initialize local SQLite database"
	@echo "  make test          Run full test suite (AST security + E2E integration)"
	@echo "  make test-unit     Run AST validator security unit tests"
	@echo "  make test-e2e      Run full pipeline end-to-end integration tests"
	@echo "  make run           Launch Streamlit web application on port $(PORT)"
	@echo "  make run-cli       Run smoke test query in terminal"
	@echo "  make docker-build  Build Docker image without starting"
	@echo "  make docker-up     Build and launch containerized engine in background on port $(PORT)"
	@echo "  make docker-down   Stop and remove running Docker containers"
	@echo "  make clean         Remove virtual cache files and build artifacts"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

init-db:
	$(PYTHON) scripts/init_db.py

test-unit:
	$(PYTHON) -m unittest tests/test_ast_validator.py -v

test-e2e:
	$(PYTHON) -m unittest tests/test_end_to_end.py -v

test: test-unit test-e2e

run:
	@if [ ! -f "data/enterprise.db" ]; then \
		echo "[!] Database not found. Initializing..."; \
		$(MAKE) init-db; \
	fi
	$(STREAMLIT) run app.py --server.port=$(PORT)

run-cli:
	$(PYTHON) src/engine.py

docker-build:
	docker compose build

docker-up:
	docker compose up --build -d
	@echo "[+] Application running at http://localhost:$(PORT)"

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete