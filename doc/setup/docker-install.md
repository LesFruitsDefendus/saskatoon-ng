# Docker Installation Guide

This guide provides instructions for setting up Saskatoon using Docker, which is the recommended approach for development.

## Quick Start with Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Start the application:

```bash
docker-compose up
```

3. Access the application at http://localhost:8000. You will have a login available with dev@dev.com and password "dev".

## What's Included

The Docker setup includes:

- Python 3.9 environment
- MySQL database
- All required system dependencies
- Performs a DB migration

## Other notes

To run commands on the app prepend your command with `docker-compose exec web`. E.g. for unit tests run `docker-compose exec web python -m pytest saskatoon/unittests -s`.

To bring down the whole docker setup and start fresh again, use `docker-compose down -v`.

By default, Docker uses its own MySQL container, but you can connect to a local (or hosted) database instead by creating a `saskatoon/.env` file from `saskatoon/env.template` and setting `SASKATOON_DB_HOST=local` (use 'local', not 'localhost', as it's specially configured to reach your host machine).

### Troubleshooting: MySQL privileges when using a local DB

If connecting from Docker to your local MySQL fails with `Host 'X.X.X.X' is not allowed to connect`, grant privileges for non-localhost connections (use your `SASKATOON_DB_USER`):

```sql
CREATE USER '<user>'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON saskatoon_dev.* TO '<user>'@'%';
FLUSH PRIVILEGES;
```

You can also grant to the container's specific IP (e.g. `'<user>'@'172.18.0.4'`).
