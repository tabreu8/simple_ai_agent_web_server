.PHONY: test test-unit test-integration test-api test-coverage test-watch install-test-deps clean-test help

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)FastAPI Application Test Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install-test-deps: ## Install testing dependencies
	@echo "$(BLUE)Installing test dependencies...$(NC)"
	pip install pytest pytest-asyncio requests httpx

test: ## Run all tests with server startup
	@echo "$(BLUE)Running full test suite with server startup...$(NC)"
	python run_tests.py

test-unit: ## Run only unit tests (without server)
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/test_knowledge_base.py -v -m "not integration"

test-api: ## Run API tests (requires server)
	@echo "$(BLUE)Running API tests...$(NC)"
	pytest tests/test_docs_api.py tests/test_agent_api.py -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/ -v -m "integration"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pip install coverage pytest-cov
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pip install pytest-watch
	ptw tests/ --runner "pytest -v"

test-specific: ## Run specific test file (usage: make test-specific FILE=test_docs_api.py)
	@echo "$(BLUE)Running specific test file: $(FILE)$(NC)"
	pytest tests/$(FILE) -v

test-fast: ## Run tests without server startup (for development)
	@echo "$(BLUE)Running tests without server startup...$(NC)"
	@echo "$(YELLOW)Note: API tests may fail without running server$(NC)"
	pytest tests/ -v

clean-test: ## Clean test artifacts and temporary files
	@echo "$(BLUE)Cleaning test artifacts...$(NC)"
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Test artifacts cleaned$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	flake8 tests/ --max-line-length=120
	black --check tests/

format: ## Format test code
	@echo "$(BLUE)Formatting test code...$(NC)"
	black tests/
	isort tests/

# Development shortcuts
dev-test: clean-test test ## Clean and run all tests
quick-test: test-fast ## Quick test run for development

# CI/CD targets
ci-test: install-test-deps test-coverage ## Run tests for CI/CD

# Default target
.DEFAULT_GOAL := help
