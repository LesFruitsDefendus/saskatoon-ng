# Docker Installation Guide

This guide provides instructions for setting up Saskatoon using Docker, which is the recommended approach for development.

## Quick Start with Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Start the application:

```bash
docker-compose up
```

3. Access the application at http://localhost:8000. You will have a login available with dev@dev.com and password "dev".

## Other notes

To run commands on the app prepend your command with `docker-compose exec web`. E.g. for unit tests run `docker-compose exec web python -m pytest saskatoon/unittests -s`.

By default, Docker uses its own MySQL container, but you can connect to a local (or hosted) database instead by creating a `saskatoon/.env` file from `saskatoon/env.template` and setting `SASKATOON_DB_HOST=local` (use 'local', not 'localhost', as it's specially configured to reach your host machine). 

To bring down the whole docker setup and start fresh again, use `docker-compose down -v`.

## What's Included

The Docker setup includes:

- Python 3.9 environment
- MySQL database
- Redis server
- All required system dependencies
- Performs a DB migration 