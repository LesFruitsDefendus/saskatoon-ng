#!/bin/bash
set -e

# 1. Check if .env exists; if not, create it from template
if [ ! -f /app/saskatoon/.env ]; then
    echo "Creating .env from template"
    cp /app/saskatoon/env.template /app/saskatoon/.env
fi

# 2. Check if requirements are installed (e.g., by checking for a known package)
if ! python -c "import django" &> /dev/null; then
    echo "Dependencies not found. Installing..."
    pip install --no-cache-dir .
    pip install --no-cache-dir '.[test]'
    python saskatoon/manage.py migrate
else
    echo "Dependencies already installed. Skipping pip install."
fi

exec python saskatoon/manage.py runserver 0.0.0.0:8000
