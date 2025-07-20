#!/bin/bash
set -e

# Check if requirements are installed (e.g., by checking for a known package)
if ! python -c "import django" &> /dev/null; then
    echo "Dependencies not found. Installing..."
    pip install --no-cache-dir '.[test]'
    python saskatoon/manage.py migrate
    saskatoon/fixtures/init
    # Wait for database to be ready and grant privileges needed for tests to work
    echo "Waiting for database to be ready..."
    while ! mysql -h db -u root -proot -e "SELECT 1" &> /dev/null; do
        echo "Database not ready yet, waiting..."
        sleep 2
    done
    echo "Granting database privileges..."
    mysql -h db -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'saskatoon'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"
else
    echo "Dependencies already installed. Skipping pip install."
fi

exec python saskatoon/manage.py runserver 0.0.0.0:8000
