## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

DEFAULT_AI_MODEL=claude-sonnet-4.6
LOGO_FILE=.rhiza/assets/rhiza-logo.svg
GH_AW_ENGINE ?= copilot  # Default AI engine for gh-aw workflows (copilot, claude, or codex)

# Always include the Rhiza API (template-managed)
include .rhiza/rhiza.mk

# Optional: developer-local extensions (not committed)
-include local.mk

## Custom targets

.PHONY: pdoc

pdoc: ## generate API documentation with pdoc
	@printf "${BLUE}[INFO] Generating API documentation with pdoc...${RESET}\n"
	@mkdir -p $(BOOK_OUTPUT)/api
	@${UV_BIN} run pdoc src/tinycta -o $(BOOK_OUTPUT)/api
	@printf "${GREEN}[SUCCESS] API documentation generated at $(BOOK_OUTPUT)/api/${RESET}\n"

book:: ## extend book build with pdoc API documentation
	@${UV_BIN} run pdoc src/tinycta -o $(BOOK_OUTPUT)/api
