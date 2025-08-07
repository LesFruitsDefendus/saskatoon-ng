#!/bin/bash

# This scripts checks if migration files are up to date.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

output=$(python3 $DIR/../saskatoon/manage.py makemigrations)

if [ "$output" != "No changes detected" ]; then
    echo "Migrations are not up to date: $output"
    exit 1
else
    echo "OK"
    exit 0
fi
