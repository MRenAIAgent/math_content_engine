.PHONY: help test test-unit test-data-service test-e2e test-e2e-live test-all test-cov lint fmt typecheck docker-build docker-test deploy deploy-dry-run deploy-gemini deploy-claude deploy-deepseek

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test: ## Run unit + data-service tests (no API key needed)
	python -m pytest tests/ -m "not e2e and not slow" -v

test-unit: ## Run only unit tests (fast, no I/O)
	python -m pytest tests/ -m "not e2e and not slow" \
		--ignore=tests/test_e2e_personalized_data_service.py \
		--ignore=tests/test_api.py -v

test-data-service: ## Run personalized-content + data-service e2e tests (mocked LLM, real SQLite)
	python -m pytest tests/test_e2e_personalized_data_service.py -v

test-e2e: ## Run all e2e-marked tests that can run without API keys
	python -m pytest tests/test_e2e_personalized_data_service.py -v -k "not TestRealPersonalizedE2E"

test-e2e-live: ## Run live e2e tests (requires ANTHROPIC_API_KEY or OPENAI_API_KEY)
	python -m pytest tests/ -m e2e -v

test-all: ## Run the full test suite including slow tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	python -m pytest tests/ -m "not e2e and not slow" \
		--cov=math_content_engine --cov-report=term-missing --cov-report=html

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------

lint: ## Run ruff linter
	python -m ruff check src/ tests/

fmt: ## Format code with black + ruff
	python -m black src/ tests/
	python -m ruff check --fix src/ tests/

typecheck: ## Run mypy type checker
	python -m mypy src/math_content_engine/

# ---------------------------------------------------------------------------
# Docker & Deployment
# ---------------------------------------------------------------------------

docker-build: ## Build Docker image for amd64 (Cloud Run compatible)
	docker buildx build --platform linux/amd64 -t math-content-engine:local -f docker/Dockerfile.engine --load .

docker-build-local: ## Build Docker image for local arch (fast, for testing)
	docker build -t math-content-engine:local -f docker/Dockerfile.engine .

docker-test: docker-build-local ## Build and test Docker image locally
	@echo "Starting container..."
	@docker rm -f mce-local-test 2>/dev/null || true
	@docker run -d --name mce-local-test -p 19090:8080 math-content-engine:local
	@sleep 3
	@echo "Health check..."
	@curl -sf http://localhost:19090/health && echo " OK" || echo " FAILED"
	@echo "Playground check..."
	@curl -sf -o /dev/null -w "HTTP %{http_code}" http://localhost:19090/playground/ && echo " OK" || echo " FAILED"
	@docker rm -f mce-local-test

deploy: ## Deploy playground to GCP Cloud Run
	bash scripts/deploy-playground.sh

deploy-dry-run: ## Preview deployment commands without executing
	bash scripts/deploy-playground.sh --dry-run

deploy-skip-build: ## Redeploy using existing image (fast)
	bash scripts/deploy-playground.sh --skip-build --skip-push

deploy-gemini: ## Deploy with Gemini (Vertex AI, uses GCP credits)
	bash scripts/deploy-playground.sh --provider gemini

deploy-claude: ## Deploy with Claude (Anthropic API key)
	bash scripts/deploy-playground.sh --provider claude

deploy-deepseek: ## Deploy with DeepSeek (deepseek-reasoner)
	bash scripts/deploy-playground.sh --provider deepseek
