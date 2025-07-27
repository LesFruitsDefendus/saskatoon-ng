#!/bin/bash
set -e

# Handle .env file precedence
# the web container has its default env vars, but we can override and extend them with the .env file if needed
if [ ! -f /app/saskatoon/.env ]; then
    echo "No .env file found, creating one from template..."
    # a .env file must exist (even if empty file), otherwise the app will fail to start
    cp /app/saskatoon/env.template /app/saskatoon/.env
fi
set -a && . /app/saskatoon/.env && set +a
echo "Loaded environment variables from .env file"

echo "Ensuring dependencies are up to date..."
pip install --no-cache-dir '.[test]'


# Wait for database to be ready and grant privileges needed for tests to work
echo "Waiting for database to be ready..."
while ! mysql -h db -u root -proot -e "SELECT 1" &> /dev/null; do
    echo "Database not ready yet, waiting..."
    sleep 2
done

echo "Running database migrations and initializing fixtures..."
saskatoon/fixtures/init

echo "Granting database privileges..."
mysql -h db -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'saskatoon'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"

{
    export DJANGO_SUPERUSER_EMAIL=dev@dev.com
    export DJANGO_SUPERUSER_PASSWORD=dev
    python saskatoon/manage.py createsuperuser --noinput
} || {
    echo "Failed to create superuser. Possibly because it already exists. Check the logs for more information."
}

exec python saskatoon/manage.py runserver 0.0.0.0:8000
