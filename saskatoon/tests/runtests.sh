#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR=$( dirname "${SCRIPT_DIR}" )
ROOT_DIR=$( dirname "${PROJECT_DIR}" )

# setting test DB env
echo "Creating testing DB ..."

# Run tests with fresh DB
[[ -e $PROJECT_DIR/.env ]] && cp $PROJECT_DIR/.env $PROJECT_DIR/.env.copy
set +e # we don;t want to leave testing DB no matter what, so we'rediabling set -e for the following statements

# Init DB
rm -f "$ROOT_DIR/saskatoon-runtests-sqlite3.db"
"$SCRIPT_DIR/newenvfile.py" "$ROOT_DIR/saskatoon-runtests-sqlite3.db" --admin-pass testing1234 --admin-email admin@example.com > "$PROJECT_DIR/.env"
"$ROOT_DIR/saskatoon/tests/createtestsuperuser.py" admin@example.com testing1234
"$ROOT_DIR/saskatoon/fixtures/init"

# Start a server in the background
python3 "$PROJECT_DIR/manage.py" runserver 8000 &
testserverpid=$!

set -e
# Kill it when the script exits
trap "kill $testserverpid; [[ -e $PROJECT_DIR/.env.copy ]] && mv $PROJECT_DIR/.env.copy $PROJECT_DIR/.env" EXIT

echo "Starting tests in a bit ..."

# Give saskatoon 5 seconds to startup
sleep 5

cd "$PROJECT_DIR"

# Launch the test. 
python3 -m pytest -vv
