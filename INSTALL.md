# Installation Guide

This guide provides instructions for setting up Saskatoon using Docker, which is the recommended approach for development.

## Quick Start with Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Start the application:

```bash
docker-compose up --build
```

3. In a new terminal, create a superuser:

```bash
docker-compose exec web python saskatoon/manage.py createsuperuser
```

4. Access the application at http://localhost:8000

5. On subsequent runs just use `docker-compose up`.

## What's Included

The Docker setup includes:

- Python 3.9 environment
- MySQL database
- Redis server
- All required system dependencies
- Performs a DB migration

## Alternative Installation

If you prefer to install Saskatoon directly on your system, please refer to the [local installation guide](doc/local-install.md).
