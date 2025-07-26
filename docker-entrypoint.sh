#!/bin/bash
set -e

echo "Ensuring dependencies are up to date..."
pip install --no-cache-dir '.[test]'

echo "Running database migrations..."
python saskatoon/manage.py migrate

echo "Initializing fixtures..."
saskatoon/fixtures/init

# Wait for database to be ready and grant privileges needed for tests to work
echo "Waiting for database to be ready..."
while ! mysql -h db -u root -proot -e "SELECT 1" &> /dev/null; do
    echo "Database not ready yet, waiting..."
    sleep 2
done

echo "Granting database privileges..."
mysql -h db -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'saskatoon'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"

exec python saskatoon/manage.py runserver 0.0.0.0:8000
