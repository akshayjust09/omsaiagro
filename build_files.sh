#!/bin/bash
set -e
echo "=== BUILD START ==="

# Ensure target directory exists
mkdir -p staticfiles_build

# Install dependencies using uv or pip with --break-system-packages
if command -v uv >/dev/null 2>&1; then
    echo "Installing dependencies using uv..."
    uv pip install --system -r requirements.txt
fi

python3 -m pip install --break-system-packages -r requirements.txt || true

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "=== BUILD END ==="
