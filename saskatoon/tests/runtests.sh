#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR=$( dirname "${SCRIPT_DIR}" )

virtualdisplaypid=0
if [[ -n "$(cat $PROJECT_DIR/.env | grep 'SASKATOON_TEST_USE_VIRTUAL_DISPLAY=yes')" ]]; then
    # Start a virtual display in the background
    python3 "$PROJECT_DIR/tests/startvirtualdisplay.py" &
    virtualdisplaypid=$!
fi

# Start a server in the background
python3 "$PROJECT_DIR/manage.py" runserver 8000 &
testserverpid=$!

# Kill it when the script exits
trap "kill $testserverpid; [[ $virtualdisplaypid -ne 0 ]] && kill $virtualdisplaypid" EXIT

echo "Starting tests in a bit ..."

# Give saskatoon 5 seconds to startup
sleep 5

cd "$PROJECT_DIR"

# Launch the test. 
python3 -m pytest
