FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    default-mysql-client \
    libtiff-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libcharls2 \
    gettext \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# No need to copy the project files or pip install
# because docker-compose sets a bind mount

# Expose port for Django
EXPOSE 8000

# Command to run the development server
CMD ["bash", "./docker-entrypoint.sh"]
