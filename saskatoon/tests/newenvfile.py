#!/usr/bin/env python3
"""
Command to create a new .env file based on a given sqlite_db_path.
"""


import string
import sys
import pathlib
import uuid

template = string.Template("""
SASKATOON_SECRET_KEY='$secret_key'
SASKATOON_DEBUG='yes'
SASKATOON_DB_ENGINE='django.db.backends.sqlite3'
SASKATOON_DB_NAME='$sqlite_db_path'
SASKATOON_TIME_ZONE='America/Toronto'
SASKATOON_TEST_WEBDRIVER=Chrome
SASKATOON_URL=http://localhost:8000
SASKATOON_ADMIN_EMAIL=
SASKATOON_ADMIN_PASSWORD=
""")

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: saskatoon/tests/newenvfile.py <sqlite_db_path> > saskatoon/new.env")
        exit(1)
    
    db_path = pathlib.Path(sys.argv[1]).absolute()

    print(template.substitute({
        'secret_key': uuid.uuid4(),
        'sqlite_db_path': db_path.as_posix(),
    }))
