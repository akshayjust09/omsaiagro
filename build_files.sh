#!/bin/bash
set -e
echo "=== BUILD START ==="

mkdir -p staticfiles_build

if command -v uv >/dev/null 2>&1; then
    echo "Creating Python 3.12 virtual environment with uv..."
    uv venv --python 3.12 .venv_build
    source .venv_build/bin/activate
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
else
    echo "Using python3..."
    python3 -m pip install --break-system-packages -r requirements.txt
    python3 manage.py collectstatic --noinput --clear
fi

echo "=== BUILD END ==="
