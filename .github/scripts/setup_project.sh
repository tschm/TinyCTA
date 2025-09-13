#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Configuration (can be overridden)
# -----------------------------
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
RENDER_FILE="${RENDER_FILE:-tests/resources/render.yml}"

# -----------------------------
# 1 Install uv
# -----------------------------
echo "Installing uv..."
pip install --upgrade pip
pip install uv

# -----------------------------
# 2 Render the project (Copier)
# -----------------------------
if [[ -f "$RENDER_FILE" && -s "$RENDER_FILE" ]]; then
    echo "Rendering project with Copier..."
    pip install copier
    copier copy . . --data-file "$RENDER_FILE" --force --overwrite --quiet

    # Cleanup leftover template files
    find . -type f -name "*.jinja" -exec rm -f {} + || true
    find . -depth -type d -name "*{{*}}*" -exec rm -rf {} + || true
fi

# -----------------------------
# 3 Check for pyproject.toml
# -----------------------------
if [[ -f "pyproject.toml" ]]; then
    echo "PYPROJECT_EXISTS=true"
    export PYPROJECT_EXISTS=true
    # Export to GitHub Actions environment if running in GitHub Actions
    if [[ -n "${GITHUB_ENV:-}" ]]; then
        echo "PYPROJECT_EXISTS=true" >> $GITHUB_ENV
    fi
else
    echo "PYPROJECT_EXISTS=false"
    export PYPROJECT_EXISTS=false
    # Export to GitHub Actions environment if running in GitHub Actions
    if [[ -n "${GITHUB_ENV:-}" ]]; then
        echo "PYPROJECT_EXISTS=false" >> $GITHUB_ENV
    fi
fi

# -----------------------------
# 4 Build virtual environment
# -----------------------------
echo "Creating virtual environment..."
uv venv --python "$PYTHON_VERSION"

# -----------------------------
# 5 Sync dependencies (if pyproject.toml exists)
# -----------------------------
if [[ "$PYPROJECT_EXISTS" == "true" ]]; then
    echo "Syncing dependencies with uv..."
    uv sync --all-extras
else
    echo "No pyproject.toml found, skipping package sync."
fi

# -----------------------------
# 6 Install task
# -----------------------------
uv pip install go-task-bin
uv run task --version

uv pip install uv


echo "Setup completed."
