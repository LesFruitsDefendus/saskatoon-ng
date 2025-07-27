# Docker Installation Guide

This guide provides instructions for setting up Saskatoon using Docker, which is the recommended approach for development.

## Quick Start with Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Start the application:

```bash
docker-compose up
```

3. Access the application at http://localhost:8000. You will have a login available with dev@dev.com and password "dev".

## Database Configuration

By default, the Docker setup uses a MySQL container included in the docker-compose stack. However, you can also connect to a local database running on your host machine.

### Option 1: Use Docker MySQL (Default)

No additional configuration needed. The application will connect to the MySQL container automatically using the default environment variables.

### Option 2: Connect to Local/Host Database

If you want to connect to a MySQL database running on your host machine instead of the Docker container:

1. Create a `.env` file in the `saskatoon/` directory by copying `saskatoon/env.template`.

2. Edit `saskatoon/.env` and set the database host to `local`:

```bash
SASKATOON_DB_ENGINE=django.db.backends.mysql
SASKATOON_DB_NAME=your_database_name
SASKATOON_DB_USER=your_username
SASKATOON_DB_PASSWORD=your_password
SASKATOON_DB_HOST=local  # Important: use 'local', not 'localhost' or '127.0.0.1'
```

**Why `local` instead of `localhost`?**

Inside Docker containers, `localhost` and `127.0.0.1` refer to the container's internal network, not your host machine. The docker-compose.yml includes an `extra_hosts` mapping that makes `local` resolve to your host machine's IP address.

## Other notes

To run commands on the app prepend your command with `docker-compose exec web`. E.g. for unit tests run `docker-compose exec web python -m pytest saskatoon/unittests -s`.

To bring down the whole docker setup and start fresh again, use `docker-compose down -v`.

## What's Included

The Docker setup includes:

- Python 3.9 environment
- MySQL database
- Redis server
- All required system dependencies
- Performs a DB migration 