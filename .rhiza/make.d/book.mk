## book.mk - Book-building targets (MkDocs-based)

ROOT := $(shell git rev-parse --show-toplevel)

.PHONY: book serve test benchmark stress hypothesis-test _book-reports _book-notebooks

# No-op stubs — overridden by test.mk / bench.mk when present
test:: ; @:
benchmark:: ; @:
stress:: ; @:
hypothesis-test:: ; @:

BOOK_OUTPUT ?= _book

# Additional uvx --with packages to inject into mkdocs build and serve.
# Projects can extend the package list without editing this template, e.g.:
#   MKDOCS_EXTRA_PACKAGES = --with "mkdocs-graphviz"
MKDOCS_EXTRA_PACKAGES ?=

##@ Book

_book-reports: test benchmark stress hypothesis-test
	@if [ -d "${ROOT}/_tests" ] && [ -n "$$(ls -A "${ROOT}/_tests" 2>/dev/null)" ]; then \
	  printf "${BLUE}[INFO] Copying ${ROOT}/_tests -> docs/reports${RESET}\n"; \
	  mkdir -p ${ROOT}/docs/reports; cp -r "${ROOT}/_tests/." "${ROOT}/docs/reports/"; \
	else \
	  printf "${YELLOW}[WARN] ${ROOT}/_tests not found or empty, skipping${RESET}\n"; \
	fi

# Export each Marimo notebook to a self-contained HTML file under docs/notebooks/.
# Skipped silently when MARIMO_FOLDER is not set or does not exist.
_book-notebooks:
	#@rm -rf ${ROOT}/docs/notebooks
	#@mkdir -p ${ROOT}/docs/notebooks

	@if [ -d "$(MARIMO_FOLDER)" ]; then \
	  printf "${BLUE}[INFO] Exporting Marimo notebooks from $(MARIMO_FOLDER)${RESET}\n"; \
	  for nb in $(MARIMO_FOLDER)/*.py; do \
	    name=$$(basename "$$nb" .py); \
	    printf "${BLUE}[INFO] Exporting $$nb -> ${ROOT}/docs/notebooks/$$name.html${RESET}\n"; \
	    abs_output="${ROOT}/docs/notebooks/$$name.html"; \
	    (cd "$$(dirname "$$nb")" && ${UV_BIN} run marimo export html --sandbox "$$(basename "$$nb")" -o "$$abs_output"); \
	  done; \
	else \
	  printf "${YELLOW}[WARN] MARIMO_FOLDER not set or missing, skipping notebook export${RESET}\n"; \
	fi

# Serve the built book locally on port 8000.
# Uses Python's built-in HTTP server so the JetBrains built-in server (which
# refuses to serve gitignored directories like _book) is not needed.
serve: book ## build and serve the book at http://localhost:8000
	@printf "${BLUE}[INFO] Serving book at http://localhost:8000 (Ctrl-C to stop)${RESET}\n"
	@cd $(BOOK_OUTPUT) && python3 -m http.server 8000

book:: _book-reports _book-notebooks ## compile the companion book via MkDocs
	@rm -rf "$(BOOK_OUTPUT)"
	# @${UVX_BIN} --with "mkdocs-material<10.0" --with "pymdown-extensions>=10.0" --with "mkdocs<2.0" $(MKDOCS_EXTRA_PACKAGES) mkdocs build -f "${ROOT}/mkdocs.yml" -d "$$(pwd)/$(BOOK_OUTPUT)"
	@${UVX_BIN} zensical build -f "$(ROOT)/mkdocs.yml"
	@touch "$(BOOK_OUTPUT)/.nojekyll"
	@printf "${GREEN}[SUCCESS] Book built at $(BOOK_OUTPUT)/${RESET}\n"
	@tree $(BOOK_OUTPUT)

