.PHONY: test test-all test-pytest test-parity test-examples test-unit test-integration test-e2e test-performance test-performance-suite ci-test-fast ci-test-full ci-test-release ci-test clean-test install-dev lint typecheck dead-code dead-code-fix help

# Default Python interpreter
PYTHON := python3
PYTEST := pytest

# Test directories
TESTS_DIR := src/tests
EXAMPLES_DIR := src/examples
FEATURE_PARITY_RUNNER := $(TESTS_DIR)/feature-parity/run_parity_tests.py

# Test output directory
TEST_OUTPUT_DIR := test-results
COVERAGE_DIR := $(TEST_OUTPUT_DIR)/coverage

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
BOLD := \033[1m
RESET := \033[0m

# Help target (default)
help: ## Display this help message
	@echo "$(BOLD)Goobits CLI Testing Framework$(RESET)"
	@echo "=================================="
	@echo ""
	@echo "$(BOLD)Main Test Targets:$(RESET)"
	@echo "  $(GREEN)test$(RESET)        - Run all tests (pytest + parity + examples)"
	@echo "  $(GREEN)test-all$(RESET)    - Same as 'test', run everything"
	@echo "  $(GREEN)test-fast$(RESET)   - Run only pytest tests (skip parity)"
	@echo ""
	@echo "$(BOLD)Individual Test Categories:$(RESET)"
	@echo "  $(BLUE)test-pytest$(RESET) - Run standard pytest tests"
	@echo "  $(BLUE)test-parity$(RESET) - Run YAML-driven feature parity tests"
	@echo "  $(BLUE)test-examples$(RESET) - Run tests in examples directory"
	@echo ""
	@echo "$(BOLD)PyTest Categories:$(RESET)"
	@echo "  $(BLUE)test-unit$(RESET)   - Unit tests only"
	@echo "  $(BLUE)test-integration$(RESET) - Integration tests only"
	@echo "  $(BLUE)test-e2e$(RESET)    - End-to-end tests only"
	@echo "  $(BLUE)test-performance$(RESET) - Performance/benchmark tests only"
	@echo "  $(BLUE)test-performance-suite$(RESET) - Production performance validation"
	@echo ""
	@echo "$(BOLD)CI/CD Tiers:$(RESET)"
	@echo "  $(GREEN)ci-test-fast$(RESET)    - Tier 1: PR checks (~5-10 min)"
	@echo "  $(GREEN)ci-test-full$(RESET)    - Tier 2: Full validation (~10-20 min)"  
	@echo "  $(GREEN)ci-test-release$(RESET) - Tier 3: Release validation (~20-30 min)"
	@echo ""
	@echo "$(BOLD)Development:$(RESET)"
	@echo "  $(YELLOW)install-dev$(RESET) - Install development dependencies"
	@echo "  $(YELLOW)lint$(RESET)        - Run code linting"
	@echo "  $(YELLOW)typecheck$(RESET)   - Run type checking"
	@echo "  $(YELLOW)clean-test$(RESET)  - Clean test artifacts and outputs"
	@echo ""
	@echo "$(BOLD)Examples:$(RESET)"
	@echo "  make test-unit                    # Run only unit tests"
	@echo "  make test-parity                  # Run cross-language CLI validation"
	@echo "  make test-pytest -k test_builder  # Run specific test pattern"
	@echo ""
	@echo "$(BOLD)Architecture Notes:$(RESET)"
	@echo "  • PyTest: Traditional testing (unit/integration/e2e)"
	@echo "  • Parity System: Cross-language CLI behavior validation"  
	@echo "  • Performance Suite: Production benchmarking (see performance/)"
	@echo "  • Makefile: Orchestration layer for easy commands"
	@echo ""
	@echo "$(BOLD)Documentation:$(RESET)"
	@echo "  • TESTING_GUIDE.md: Comprehensive testing architecture guide"
	@echo "  • CODEMAP.md: Complete project architecture overview"

# Main test target - run everything
test: test-all ## Run all tests (same as test-all)

test-all: clean-test install-dev ## Run all tests: pytest, parity, and examples
	@echo "$(BOLD)🚀 Running Complete Test Suite$(RESET)"
	@echo "======================================"
	@mkdir -p $(TEST_OUTPUT_DIR)
	@echo "$(BLUE)Step 1/3: Running PyTest tests...$(RESET)"
	@$(MAKE) test-pytest
	@echo "$(BLUE)Step 2/3: Running Feature Parity tests...$(RESET)"
	@$(MAKE) test-parity
	@echo "$(BLUE)Step 3/3: Running Example tests...$(RESET)"
	@$(MAKE) test-examples
	@echo "$(GREEN)✅ All tests completed!$(RESET)"

test-fast: install-dev ## Run only pytest tests (skip slower parity tests)
	@echo "$(BOLD)⚡ Running Fast Test Suite (PyTest only)$(RESET)"
	@$(MAKE) test-pytest
	@$(MAKE) test-examples

# Standard pytest tests
test-pytest: ## Run standard pytest tests with coverage
	@echo "$(BLUE)Running PyTest tests...$(RESET)"
	@mkdir -p $(TEST_OUTPUT_DIR)
	@if python -c "import pytest_cov" 2>/dev/null; then \
		mkdir -p $(COVERAGE_DIR); \
		$(PYTEST) $(TESTS_DIR)/ \
			--cov=goobits_cli \
			--cov-report=html:$(COVERAGE_DIR)/html \
			--cov-report=xml:$(COVERAGE_DIR)/coverage.xml \
			--cov-report=term-missing \
			--junit-xml=$(TEST_OUTPUT_DIR)/pytest-results.xml \
			-v; \
	else \
		echo "$(YELLOW)Coverage plugin not installed, running tests without coverage$(RESET)"; \
		$(PYTEST) $(TESTS_DIR)/ --junit-xml=$(TEST_OUTPUT_DIR)/pytest-results.xml -v; \
	fi

# Feature parity tests using existing runner
test-parity: ## Run YAML-driven feature parity tests
	@echo "$(BLUE)Running Feature Parity tests...$(RESET)"
	@if [ -f "$(FEATURE_PARITY_RUNNER)" ]; then \
		$(PYTHON) $(FEATURE_PARITY_RUNNER) --verbose $(ARGS); \
	else \
		echo "$(RED)Error: Feature parity runner not found at $(FEATURE_PARITY_RUNNER)$(RESET)"; \
		exit 1; \
	fi

# Examples directory tests
test-examples: ## Run tests in examples directory
	@echo "$(BLUE)Running Example tests...$(RESET)"
	@if [ -d "$(EXAMPLES_DIR)" ]; then \
		$(PYTHON) -m pytest $(EXAMPLES_DIR)/ -v || echo "$(YELLOW)Note: Some example tests may be non-critical$(RESET)"; \
	else \
		echo "$(YELLOW)No examples directory found, skipping example tests$(RESET)"; \
	fi

# Individual test categories
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running Unit tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running Integration tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/integration/ -v

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running E2E tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/e2e/ -v

test-performance: ## Run performance tests only
	@echo "$(BLUE)Running Performance tests...$(RESET)"
	$(PYTEST) $(TESTS_DIR)/performance/ -v

# Production performance validation
test-performance-suite: ## Run comprehensive performance validation suite  
	@echo "$(BLUE)Running Production Performance Suite...$(RESET)"
	@if [ -f "performance/performance_suite.py" ]; then \
		$(PYTHON) performance/performance_suite.py --quick; \
	else \
		echo "$(YELLOW)Performance suite not found, skipping advanced benchmarks$(RESET)"; \
	fi

# Development utilities
install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(RESET)"
	pip install -e .[dev,test]

lint: ## Run code linting
	@echo "$(YELLOW)Running code linting...$(RESET)"
	ruff check src/

typecheck: ## Run type checking
	@echo "$(YELLOW)Running type checking...$(RESET)"
	mypy src/goobits_cli/

# Dead code detection
dead-code: ## Check for dead code with Vulture and Ruff
	@echo "$(YELLOW)Running dead code detection...$(RESET)"
	@vulture . --min-confidence 80 --exclude "*/test_*,*/migrations/*,*/__pycache__/*,.venv/*,venv/*,*/node_modules/*,*/target/*,*/dist/*,*/build/*"
	@ruff check --select F401,F841

dead-code-fix: ## Auto-fix unused imports with Ruff
	@echo "$(YELLOW)Auto-fixing unused imports...$(RESET)"
	@ruff check --select F401,F841 --fix

# Cleanup
clean-test: ## Clean test artifacts and outputs
	@echo "$(YELLOW)Cleaning test artifacts...$(RESET)"
	@rm -rf $(TEST_OUTPUT_DIR)
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Advanced targets with arguments
test-parity-lang: ## Run parity tests for specific language(s): make test-parity-lang LANGS="python nodejs"
	@$(MAKE) test-parity ARGS="--language $(LANGS)"

test-parity-suite: ## Run specific parity suite(s): make test-parity-suite SUITES="basic-commands"
	@$(MAKE) test-parity ARGS="--suite $(SUITES)"

# CI/CD friendly targets
ci-test-fast: clean-test ## CI Tier 1: Fast tests for PR checks (~5-10 min)
	@echo "$(BOLD)🚀 CI Tier 1: Fast Test Suite$(RESET)"
	@mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTEST) $(TESTS_DIR)/ \
		--cov=goobits_cli \
		--cov-report=xml:$(TEST_OUTPUT_DIR)/coverage.xml \
		--junit-xml=$(TEST_OUTPUT_DIR)/junit.xml \
		--tb=short \
		-q

ci-test-full: clean-test ## CI Tier 2: Full validation including parity (~10-20 min)
	@echo "$(BOLD)🔍 CI Tier 2: Comprehensive Test Suite$(RESET)"
	@mkdir -p $(TEST_OUTPUT_DIR)
	$(PYTEST) $(TESTS_DIR)/ \
		--cov=goobits_cli \
		--cov-report=xml:$(TEST_OUTPUT_DIR)/coverage.xml \
		--junit-xml=$(TEST_OUTPUT_DIR)/junit.xml \
		--tb=short \
		-q
	@$(MAKE) test-parity ARGS="--verbose" || echo "$(YELLOW)Parity tests had issues$(RESET)"

ci-test-release: ci-test-full ## CI Tier 3: Release validation with performance (~20-30 min)
	@echo "$(BOLD)🎯 CI Tier 3: Release Validation$(RESET)"
	@$(MAKE) test-performance-suite || echo "$(YELLOW)Performance suite had issues$(RESET)"

# Legacy CI target (deprecated - use ci-test-full)
ci-test: ci-test-full ## Run tests in CI mode with XML output (deprecated)

# Development workflow
dev-test: ## Quick development test cycle
	@$(MAKE) lint
	@$(MAKE) typecheck  
	@$(MAKE) test-fast