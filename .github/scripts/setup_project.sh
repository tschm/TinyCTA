#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Configuration (can be overridden)
# -----------------------------
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
RENDER_FILE="${RENDER_FILE:-tests/resources/render.yml}"

# -----------------------------
# 1️⃣ Install uv
# -----------------------------
echo "Installing uv..."
pip install --upgrade pip
pip install uv

# -----------------------------
# 2️⃣ Install Task
# -----------------------------
echo "Installing Task..."
curl -fsSL https://taskfile.dev/install.sh | sh -s -- -d -b /usr/local/bin v3.x

# -----------------------------
# 3️⃣ Render the project (Copier)
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
# 4️⃣ Check for pyproject.toml
# -----------------------------
if [[ -f "pyproject.toml" ]]; then
    echo "PYPROJECT_EXISTS=true"
    export PYPROJECT_EXISTS=true
else
    echo "PYPROJECT_EXISTS=false"
    export PYPROJECT_EXISTS=false
fi

# -----------------------------
# 5️⃣ Build virtual environment
# -----------------------------
echo "Creating virtual environment..."
uv venv --python "$PYTHON_VERSION"

# -----------------------------
# 6️⃣ Sync dependencies (if pyproject.toml exists)
# -----------------------------
if [[ "$PYPROJECT_EXISTS" == "true" ]]; then
    echo "Syncing dependencies with uv..."
    uv sync --all-extras
else
    echo "No pyproject.toml found, skipping package sync."
fi

echo "Setup completed."
