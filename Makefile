# Colors for pretty output - ANSI escape codes for colored terminal output
BLUE := \033[36m  # Cyan color for highlighting commands and targets
BOLD := \033[1m   # Bold text for headings
RESET := \033[0m  # Reset formatting

# Set the default target to run when 'make' is called without arguments
.DEFAULT_GOAL := help

# Declare phony targets (targets that don't represent files)
# This prevents conflicts with any files named the same as these targets
.PHONY: help verify install fmt test clean

##@ Development Setup
# This section contains targets for setting up the development environment

# Create a Python virtual environment using uv (a fast Python package installer and resolver)
venv:
	@printf "$(BLUE)Creating virtual environment...$(RESET)\n"
	# Download and install uv from astral.sh
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	# Create a virtual environment with Python 3.12
	@uv venv --python 3.12

# Install all project dependencies (depends on venv target)
install: venv ## Install all dependencies using uv
	@printf "$(BLUE)Installing dependencies...$(RESET)\n"
	# Synchronize dependencies from pyproject.toml, including dev dependencies and all extras
	# The --frozen flag ensures reproducible installations
	@uv sync --dev --all-extras --frozen

##@ Code Quality
# This section contains targets for maintaining code quality

# Format and lint the code using pre-commit hooks (depends on venv target)
fmt: venv ## Run code formatting and linting
	@printf "$(BLUE)Running formatters and linters...$(RESET)\n"
	# Run all pre-commit hooks on all files, regardless of git status
	@uvx pre-commit run --all-files

##@ Testing
# This section contains targets for running tests

# Run all tests in the project (depends on install target)
test: install ## Run all tests
	@printf "$(BLUE)Running tests...$(RESET)\n"
	# Install pytest without using the pip cache
	@uv pip install --no-cache-dir pytest
	# Run pytest on all tests in the tests directory
	@uv run pytest tests

##@ Cleanup
# This section contains targets for cleaning up the project

# Clean up generated files and directories
clean: ## Clean generated files and directories
	@printf "$(BLUE)Cleaning project...$(RESET)\n"
	# Use git clean to remove all untracked files that are ignored by git
	# -d: remove untracked directories
	# -X: remove only files ignored by git
	# -f: force removal
	@git clean -d -X -f

##@ Help
# This section contains targets for displaying help information

# Display help information about available targets
help: ## Display this help message
	@printf "$(BOLD)Usage:$(RESET)\n"
	@printf "  make $(BLUE)<target>$(RESET)\n\n"
	@printf "$(BOLD)Targets:$(RESET)\n"
	# Parse the Makefile to extract and display target descriptions
	# - Looks for lines with pattern: target: ## description
	# - Also formats section headers that start with ##@
	# - Uses the BLUE and BOLD colors defined at the top of the file
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-15s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BOLD)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)
