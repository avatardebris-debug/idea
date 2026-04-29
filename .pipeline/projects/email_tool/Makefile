.PHONY: help test lint format check install dev docker-build docker-run clean

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT := email_tool
VERSION := 0.1.0

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install project dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install project and development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test: ## Run tests with pytest
	$(PYTHON) -m pytest tests/ -v --cov=$(PROJECT) --cov-report=term-missing

test-coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ -v --cov=$(PROJECT) --cov-report=html --cov-report=term-missing
	@echo "Open htmlcov/index.html to view coverage report"

lint: ## Run linting checks
	$(PYTHON) -m flake8 $(PROJECT) tests/
	$(PYTHON) -m mypy $(PROJECT)

format: ## Format code with black
	$(PYTHON) -m black $(PROJECT) tests/

format-check: ## Check code formatting without modifying
	$(PYTHON) -m black --check $(PROJECT) tests/

check: ## Run all checks (test, lint, format)
	@echo "Running tests..."
	$(MAKE) test
	@echo "Running lint..."
	$(MAKE) lint
	@echo "Checking format..."
	$(MAKE) format-check

dev: ## Run in development mode with auto-reload
	$(PYTHON) -m uvicorn $(PROJECT).dashboard.app:app --reload --host 0.0.0.0 --port 8000

dev-daemon: ## Run daemon in development mode
	$(PYTHON) -m $(PROJECT).daemon --foreground

docker-build: ## Build Docker image
	docker build -t email-tool:$(VERSION) .

docker-run: ## Run Docker container
	docker run -d \
		--name email-tool \
		-p 8000:8000 \
		-v $(shell pwd)/config.yaml:/etc/email_tool/config.yaml:ro \
		-v email_tool_data:/var/lib/email_tool \
		email-tool:$(VERSION)

docker-stop: ## Stop Docker container
	docker stop email-tool || true

docker-clean: ## Remove Docker container and volumes
	docker stop email-tool || true
	docker rm email-tool || true
	docker volume rm email_tool_data || true

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	rm -f .coverage
	rm -rf coverage.xml

build: ## Build distribution packages
	$(PYTHON) -m build

install-systemd: ## Install systemd service
	sudo cp systemd/email_tool_daemon.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable email_tool_daemon
	sudo systemctl start email_tool_daemon

uninstall-systemd: ## Remove systemd service
	sudo systemctl stop email_tool_daemon
	sudo systemctl disable email_tool_daemon
	sudo rm /etc/systemd/system/email_tool_daemon.service
	sudo systemctl daemon-reload

install-cron: ## Install cron jobs
	crontab cron/email_tool_cron

uninstall-cron: ## Remove cron jobs
	crontab -r 2>/dev/null || true

docs: ## Generate documentation
	$(PYTHON) -m mkdocs build

serve-docs: ## Serve documentation locally
	$(PYTHON) -m mkdocs serve

release: ## Prepare release (update version, build, tag)
	@echo "Releasing version $(VERSION)"
	$(MAKE) clean
	$(MAKE) build
	@echo "Run: git tag v$(VERSION) && git push origin v$(VERSION)"

setup: ## Setup development environment
	@echo "Setting up development environment..."
	$(MAKE) install
	$(MAKE) install-dev
	$(MAKE) format
	@echo "Development environment ready!"

.PHONY: all
all: check
