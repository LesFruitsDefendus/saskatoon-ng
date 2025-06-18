FROM python:3.9-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    redis-server \
    libtiff5-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libcharls2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# No need to copy the project files or pip install
# because docker-compose sets a bind mount

# Expose port for Django
EXPOSE 8000

# Command to run the development server
CMD ["bash", "./docker-entrypoint.sh"] 