# Local Installation guide

Please follow each part of this documentation in order to run your own instance of Saskatoon.

## Overview
1. [Set up requirements](#requirements)
2. [Install Saskatoon](#installation)
3. [Configuration](#configuration)
   1. [Prepare `.env` settings](#.env-settings)
   2. [Set up local database](#local-database)
   3. [Set up Django](#django-setup)
4. [Launch Saskatoon server](#launch-the-saskatoon-server-on-localhost)
5. [Load sample data (fixtures)](#loading-sample-data-fixtures)
6. [Import/export database and migrate from older version of Saskatoon database](#database)
7. [Run tests](#running-tests)

## Requirements

0. Python 3.9 (included in Debian Bullseye)

1. MySQL client

    For Debian and derivatives:
    ```
    sudo apt install default-libmysqlclient-dev
    ```

    For MacOS (need first install [Homebrew](https://brew.sh/)):
    ```
    brew install mysql-client
    echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```
    Note if your MacOS version is too old, Homebrew may have trouble installing MySQL client. You can directly download and install it from the [.dmg](https://dev.mysql.com/downloads/shell/) file, then run:
    ```
    echo 'export PATH="/usr/local/mysql/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

2. Redis server

    `django-redis` is currently used as a caching backend with default configuration (see `CACHES` variable in `saskatoon/settings.py`). A Redis server must be run in the background (even when loading sample data from the fixtures).

    For Debian and derivatives:
    ```
    $ sudo apt install redis-server
    $ sudo systemctl status redis-server
    ```
    Note the Redis service will start automatically when the installation finishes (if using systemd)

    For macOS:

    Follow the instructions in [Redis docs](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/).

3. Pillow

    In normal scenario, you don't need this step, and `pip` should take care of the installation of the `Pillow` package. If you have issues with it, installing the following dependencies should help:

    For Debian and derivatives:
    ```
    sudo apt install libtiff5-dev libjpeg-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev libcharls2 redis-server
    ```

    For MacOS:
    ```
    brew install libtiff libjpeg webp little-cms2 zlib redis
    echo 'export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/usr/local/Cellar/zlib/1.2.11/lib/pkgconfig"' >> ~/.zshrc
    source ~/.zshrc
    ```

    Refer to [Pillow installation instruction](https://pillow.readthedocs.io/en/latest/installation.html#building-on-linux) for more documentation.

## Installation

1. Set up a Python virtual environment:

    It is always good practice to isolate the project related packages in a virtual environment to prevent version conflicts between projects. See more on this in [Python docs](https://docs.python.org/3/library/venv.html).

    Create and activate a virtual environment:
    ```
    $ python3 -m venv venv
    $ . venv/bin/activate
    ```

2. Install Saskatoon and its dependencies

    ```
    (venv)$ pip3 install .
    ```
    > NOTE: Don't use ``python3 setup.py install`` as it could mess up some dependencies.

    See `setup.py` for more details on the project's package requirements

## Configuration

### .env settings

Saskatoon uses `django-dotenv` to manage local environment settings. Copy the [saskatoon/env.template](saskatoon/env.template) file into `saskatoon/.env` and adapt it to your needs.

For a minimal setup, you only need to specify `SASKATOON_SECRET_KEY`. To generate a new random secret key, you can run this script:
```
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
> WARNING: since your `.env` file is solely for your local environment, always keep it out of source control (see [.gitignore](.gitignore) file).

### Local database

There are two methods for setting up a local database. SQLite can be used to get up and running quickly, but MySQL is used in production.

1. SQLite (by default in local environment as specified in `env.template`)

    To use a simple *sqlite3.db* database `SASKATOON_DB_ENGINE` must be set to `django.db.backends.sqlite3` in `.env`.

2. MySQL

    On Debian and derivatives:
    ```
    $ sudo apt install default-mysql-server
    $ sudo systemctl start mysql
    $ sudo systemctl enable mysql
    $ sudo systemctl status mysql
    $ sudo mysql_secure_installation
    ```

    To create an empty database:
    ```
    $ sudo mysql -u root -p
    > CREATE USER '<user>'@'localhost' IDENTIFIED BY '<password>';
    > SELECT user FROM mysql.user;   // show all users
    > CREATE DATABASE saskatoon_dev;
    > SHOW DATABASES;
    > GRANT ALL PRIVILEGES ON saskatoon_dev.* TO '<user>'@'localhost';
    > ALTER DATABASE saskatoon_dev CHARACTER SET utf8;

    ```

    Example mysql configuration in `.env` file:
    ```
    # Database
    SASKATOON_DB_ENGINE=django.db.backends.mysql
    SASKATOON_DB_NAME=saskatoon_dev
    SASKATOON_DB_USER=<user>
    SASKATOON_DB_PASSWORD=<password>
    SASKATOON_DB_HOST=127.0.0.1
    ```

    You can optionally configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).

    For database migrations, see [database](#database).

### Django setup

First, activate the virtual environment, if it is inactive:
```
$ . venv/bin/activate
```

#### Initiate the database:
```
(venv)$ python3 saskatoon/manage.py migrate --skip-checks
```

In case you have an error similar to this one:
```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')
```
then you need set your MySQL database to UTF-8:
```
ALTER DATABASE 'your_saskatoon_database' CHARACTER SET utf8;
```
See [Django doc: unicode data](https://docs.djangoproject.com/en/3.2/ref/unicode/) for more details.

#### Create administrator account

An administrator account allows you to access the admin panel where you can see all data of the DB and make some actions on it.

To create a new administrator account:
```
(venv)$ python3 saskatoon/manage.py createsuperuser --skip-checks
```

#### Static files

For Django to serve static files during development `SASKATOON_DEBUG` must be set to `yes` in `.env`.

This is not suitable for production, however. To collect all files from static folders (defined by `STATIC_URL` in `settings.py`) into the `STATIC_ROOT` directory:
```
(venv)$ python3 saskatoon/manage.py collectstatic
```

See [Django doc: managing static files](https://docs.djangoproject.com/en/3.2/howto/static-files/) for more details.

## Launch the Saskatoon server on localhost

_Note: A Redis server must be run in the background._

You can use Django embedded server for development purpose:
```
(venv)$ python3 saskatoon/manage.py runserver 8000
```

To access the admin panel, visit [localhost:8000/admin](http://127.0.0.1:8000/admin)


## Loading sample data (fixtures)

This is optional, but you can load some sample data (e.g. some personnel and harvest records) to play with Saskatoon.

_Note: A Redis server must be run in the background. `EMAIL_HOST` in the `.env` file need be configured properly or specified as empty string._

To load all sample data from the fixtures:
```
(venv)$ saskatoon/fixtures/init
```

For more information on fixtures, see [fixtures/README](./saskatoon/fixtures/README.md).

## Database

### Import/export MySQL database

To export a dump file of the database:
```
mysqldump -u <user> -p <db_name> > dump_file.sql
```

To import a *.sql* dump file into an **empty** database:
```
$ mysql -u <user> -p <db_name> < dump_file.sql
```

> WARNING: the database you are importing the dump file into should be **empty** and have the **same name** as the original database. To get the original database name from the dump file:
> ```
> $ head -n 5 dump_file.sql
> ```

### Migrate from old generation

To migrate MySQL database from old generation [Saskatoon](https://github.com/LesFruitsDefendus/saskatoon) project:

1. create an empty database  and import .sql dump file
    ```
    $ mysql -u root -p
    > CREATE DATABASE saskatoon_prod;
    > exit;
    $ mysql -u <user> -p saskatoon_prod < saskatoon_prod_dump.sql
    ```

2. comment out `auth` dependency in `saskatoon/member/migrations/0001_initial.py`:
    ```
    class Migration(migrations.Migration):
    
    initial = True
    
    dependencies = [
        # ('auth', '0012_alter_user_first_name_max_length'),
    ]
    
    operations = [
    ...
    ```

3. run migrations
    ```
    (venv)$ python3 saskatoon/manage.py migrate
    ```

> NOTE: `auth` dependency in `saskatoon/member/migrations/0001_initial.py` is absolutely needed for migrating from a fresh database.

## Running tests

See [saskatoon/tests/README.md](saskatoon/tests/README.md) for instructions.