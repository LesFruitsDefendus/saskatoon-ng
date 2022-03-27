# Local Installation guide

Please follow each part of this documentation in order to run your own instance of Saskatoon.

## Requirements

1. MySQL client

    For Debian and derivatives:
    ```
    sudo apt install default-libmysqlclient-dev
    ```

    For MacOS:
    ```
    brew install mysql-client
    echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

2. Python virtualenv

    To install Python requirements in a virtual environment:
    ```
    $ sudo apt install python3-dev python3-pip
    $ pip3 install virtualenv
    $ virtualenv venv
    $ . venv/bin/activate
    $(venv) pip3 install .
    ```

    See `setup.py` for more details on the project's package requirements


3. Redis server

    `django-redis` is currently used as a caching backend with default configuration (see `CACHES` variable in `saskatoon/settings.py`). A Redis server must be run in the background:
    ```
    $ sudo apt install redis-server
    $ sudo systemctl status redis-server
    ```
    Note the Redis service will start automatically when the installation finishes (if using systemd)

    [For macOS](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/).

4. Pillow

    You might run into issues when installing the `Pillow` package using `pip`, in which case installing the following dependencies should help:

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


## .env settings

Saskatoon uses `python-dotenv` to manage local environment settings. Copy the [saskatoon/env.template](saskatoon/env.template) file into `saskatoon/.env` and adapt it to your needs. 

WARNING: always keep the `.env` file out of source control (see [.gitignore](.gitignore) file).

Note: to generate a new random secret key, you can run this python script:
```
from django.core.management import utils

print(utils.get_random_secret_key())
```

## local database

1. SQLite

To use a simple *sqlite3.db* database `SASKATOON_DB_ENGINE` must be set to `django.db.backends.sqlite3` in `.env`.

You can optionally configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).


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
> GRANT ALL PRVILEGES ON saskatoon_dev.* TO '<user>'@'localhost';
> ALTER DATABASE saskatoon_dev CHARACTER SET utf8;

```

Example mysql configuration in *.env* file:
```
# Database
SASKATOON_DB_ENGINE=django.db.backends.mysql
SASKATOON_DB_NAME=saskatoon_dev
SASKATOON_DB_USER=<user>
SASKATOON_DB_PASSWORD=<password>
SASKATOON_DB_HOST=127.0.0.1
```

## Django setup

To initiate the database:
```
$ . venv/bin/activate
$(venv) python3 saskatoon/manage.py migrate --skip-checks
```

ps: in case you have an error similar to this one:
```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')
```
then you'll need to set your database to UTF-8:
```
ALTER DATABASE 'your_saskatoon_database' CHARACTER SET utf8;
```


### Create administrator account

This part is optional but you can create a new administrator account to access the admin panel.
This admin panel allows you to see all data of the DB and make some action on it.

To create a new administrator account use :
```
$(venv) python3 saskatoon/manage.py createsuperuser --skip-checks
```


### Static files

For Django to serve static files during development `SASKATOON_DEBUG` must be set to `yes`.

This is not suitable for production however. To collect all files from static folders (defined by `STATIC_URL` in `settings.py`) into the `STATIC_ROOT` directory:
```
$(venv) python3 saskatoon/manage.py collectstatic
```

See [https://docs.djangoproject.com/en/3.0/howto/static-files/](Django doc: managing static files) for more details.


### Launch the server on localhost

You can use Django embedded server for development purpose:
```
python3 saskatoon/manage.py runserver 8000
```

NB: to access the admin panel visit [localhost:8000/admin](http://127.0.0.1:8000/admin)


## Loading initial data (fixtures)

[Providing initial data for models](https://docs.djangoproject.com/en/dev/howto/initial-data/)


To initialize the database with the `saskatoon.json` dump file:
```
(venv)$ python3 saskatoon/manage.py migrate --skip-check
(venv)$ python3 saskatoon/manage.py loaddata saskatoon/fixtures/saskatoon.json
```

Alternatively you could audit/modify the individual .json files located in `saskatoon/fixtures` and run:
```
(venv)$ saskatoon/fixtures/init
```

>  Warning: each time you run loaddata, the data will be read from the fixture and re-loaded into the database. Note this means that if you change one of the rows created by a fixture and then run loaddata again, you’ll wipe out any changes you’ve made.

Note: If you get `ConnectionRefusedError: [Errno 111] Connection refused` error on `send_mail()` function it means your local mail server is not properly configured. One way to ignore this issue is to keep the `EMAIL_HOST=` variable empty in your `.env` file. (see `saskatoon/harvest/signals.py` for more details)

To load all .json files located in `saskatoon/fixtures`:
```
(venv)$ saskatoon/fixtures/loaddata all
```
Note: this does not include .json files of the type: `saskatoon*.json`


To load a single app or model instance:
```
(venv)$ saskatoon/fixtures/loaddata <instance>
```
For example, running `saskatoon/fixtures/loaddata member-city` will load the `member-city.json` file into the database.


To export all data from a pre-populated database:
```
(venv)$ saskatoon/fixtures/dumpdata
```
This will create `saksatoon/fixtures/saksatoon.json`


To export data from a specific app or table:
```
(venv)$ saskatoon/fixtures/dumpdata <app or instance>
```
For example, running `saskatoon/fixtures/dumpdata member.city` will create a `member-city.json` file containing all instances from the `City` model (defined in `members.model.py`) currently stored in the database.


## Import/export MySQL database

To export a dump file of the database:
```
mysqldump -u <user> -p <db_name> > dump_file.sql
```

To import a *.sql* dump file into an **empty** database:
```
$ mysql -u <user> -p <db_name> < dump_file.sql
```

*Warning*: was only able to import a dump file into a database of the **same name**. To get the original database name from the dump file:
```
$ head -n 5 dump_file.sql
```

## Migrate from old generation

To migrate MySQL database from old generation [saskatoon](https://github.com/LesFruitsDefendus/saskatoon) project:

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

Note: `auth` dependency in `saskatoon/member/migrations/0001_initial.py` is absolutely needed for migrating from a fresh database.


## Running tests

Install test requirements with:

```
pip3 install '.[test]'
```

Extra configuration is required in `.env` to run tests:

```
# Testing settings

SASKATOON_URL=http://localhost:8000
SASKATOON_ADMIN_EMAIL=admin@example.com
SASKATOON_ADMIN_PASSWORD=testing1234
```

Tests are located inside `saskatoon/tests` folder. 

Created a test super user with the following command:

```
python3 saskatoon/tests/createtestsuperuser.py admin@example.com testing1234
```

Then run tests with:

```
tox -e test
```

> See also [saskatoon/tests/README.md](saskatoon/tests/README.md)
