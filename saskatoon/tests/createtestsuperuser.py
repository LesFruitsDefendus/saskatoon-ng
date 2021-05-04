#!/usr/bin/env python
"""
Command to create a test super user. 
"""
if __name__ == "__main__":

    import pathlib
    import invoke
    import os
    import sys

    if len(sys.argv) != 3:
        print("Usage: createtestsuperuser.py <email> <password>")
        exit(1)

    project_dir = pathlib.Path(__file__).parent.parent.parent.absolute()

    invoke.run(f'{project_dir}/saskatoon/manage.py migrate --skip-checks', pty=True, )
    invoke.run(f'{project_dir}/saskatoon/manage.py createsuperuser', 
        pty=True, 
        watchers=[
            invoke.watchers.Responder('Email address', sys.argv[1] + '\n'),
            invoke.watchers.Responder('Password', sys.argv[2]+ '\n'),
            invoke.watchers.Responder('Bypass password validation and create user anyway?', 'y\n'),
        ], timeout=5)
