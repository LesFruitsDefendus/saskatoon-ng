#!/bin/bash

# This script checks that:
# 1. Every model has an entry in its app's PERMISSIONS dict
# 2. doc/permissions.md is up to date

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 $DIR/../saskatoon/manage.py check_permissions
if [ $? -ne 0 ]; then
    exit 1
fi

python3 $DIR/../saskatoon/manage.py export_permissions > /dev/null

if ! git diff --quiet $DIR/../doc/permissions.md; then
    echo "doc/permissions.md is not up to date. Please run 'make permissions'."
    exit 1
else
    echo "OK"
    exit 0
fi
