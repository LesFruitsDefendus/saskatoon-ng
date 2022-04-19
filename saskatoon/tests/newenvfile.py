#!/usr/bin/env python3
"""
Command to create a new .env file based on a given sqlite_db_path (for testing only).
"""
import string
import shlex
import pathlib
import uuid
import argparse

template = string.Template("""
SASKATOON_SECRET_KEY=$secret_key
SASKATOON_DEBUG=yes
SASKATOON_DB_ENGINE=django.db.backends.sqlite3
SASKATOON_DB_NAME=$sqlite_db_path
SASKATOON_TIME_ZONE=America/Toronto
SASKATOON_TEST_WEBDRIVER=Chrome
SASKATOON_URL=http://localhost:8000
SASKATOON_ADMIN_EMAIL=$admin_email
SASKATOON_ADMIN_PASSWORD=$admin_password
""")

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="Usage: saskatoon/tests/newenvfile.py <sqlite_db_path> > saskatoon/.env"
    )
    parser.add_argument('sqlite_db_path')
    parser.add_argument('--admin-email', )
    parser.add_argument('--admin-password', )
    return parser

if __name__ == "__main__":
    
    args = get_parser().parse_args()
    
    db_path = pathlib.Path(args.sqlite_db_path).absolute()
    admin_email = str(args.admin_email) or ''
    admin_password = str(args.admin_password) or ''

    mapping = {
        'secret_key': str(uuid.uuid4()),
        'sqlite_db_path': db_path.as_posix(),
        'admin_email': admin_email,
        'admin_password': admin_password,
    }

    for k in mapping:
        mapping[k] = shlex.quote(mapping[k])

    print(template.substitute(mapping))
