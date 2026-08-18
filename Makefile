## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

# No template default exists for this; without it `make mutation` sees an empty
# path, the `[ ! -d ]` guard fires, and the target silently no-ops with a warning.
MUTATION_SOURCE_FOLDER ?= src/tinycta

# Override template default: include mkdocstrings plugin for API docs, plus the
# tinycta package itself (with the optional hyper extra) so mkdocstrings/griffe
# can import the modules it documents — including tinycta.hyper and tinycta.linalg
# (which pulls in cvx-linalg). Without this the isolated uvx env lacks the package
# and the build fails with "ModuleNotFoundError: No module named 'tinycta'".
MKDOCS_EXTRA_PACKAGES = --with 'mkdocstrings[python]' --with-editable '.[hyper]'

# Always include the Rhiza API (template-managed)
include .rhiza/rhiza.mk

# Optional: developer-local extensions (not committed)
-include local.mk
