#!/bin/bash
set -e

# Load environment variables from .env file
if [ ! -f saskatoon/.env ]; then
    echo "No .env file found, creating one from template..."
    # a .env file must exist (even if empty file), otherwise the app will fail to start
    cp -p saskatoon/env.template saskatoon/.env
fi
set -a && . saskatoon/.env && set +a
echo "Loaded environment variables from .env file"

echo "Ensuring dependencies are up to date..."
pip install --no-cache-dir '.[test]'


echo "Waiting for database to be ready..."
while ! mysql -h "$SASKATOON_DB_HOST" -u "$SASKATOON_DB_USER" -p"$SASKATOON_DB_PASSWORD" -e "SELECT 1" &> /dev/null; do
    echo "Database not ready yet, waiting..."
    sleep 2
done

if [ "$SASKATOON_INIT_FIXTURES" = "true" ]; then
    echo "Running database migrations and initializing fixtures..."
    saskatoon/fixtures/init
fi

# Grant DB privileges needed for tests to work, if we're using the containerized database
if [ "$SASKATOON_DB_HOST" = "db" ]; then
    echo "Granting database privileges..."
    mysql -h "$SASKATOON_DB_HOST" -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO '$SASKATOON_DB_USER'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"
fi

# Set DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD in .env file to automatically create a superuser  
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    {
        # Uses DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD from .env file
        python saskatoon/manage.py createsuperuser --noinput
    } || {
        echo "Failed to create superuser. Possibly because it already exists. Check the logs for more information."
    }
fi

exec python saskatoon/manage.py runserver 0.0.0.0:8000
