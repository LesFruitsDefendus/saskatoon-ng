# Installation guide

Please follow each part of this documentation in order to run your own instance of Saskatoon.

## Installation of requirements

- MySQL client

    For Debian and derivatives:
    ```
    sudo apt install libmysqlclient-dev
    ```

    For MacOS:
    ```
    brew install mysql-client
    echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

- Pillow requirements

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


All Python requirements are present in the `requirements.txt` file at the project's root.

You can optionnaly use `virtualenv` to manage your dependencies.
```
virtualenv ve
. ve/bin/activate
```

To install Python requirements use :
```
pip3 install .
```

## Database and other settings

To set new settings, adapt the following ``.env`` 
file and place it inside `saskatoon/` project directory. 

```
# SECURITY WARNING: keep the secret key used in production secret!
# More infos: https://docs.djangoproject.com/fr/3.1/ref/settings/#secret-key
SASKATOON_SECRET_KEY=<KEY>

# SECURITY WARNING: don't run with debug turned on in production!
SASKATOON_DEBUG=no

# Database settings - sqlite3 (dev)
SASKATOON_DB_ENGINE=django.db.backends.sqlite3
SASKATOON_DB_NAME=/YOURDBPATH/sqlite3.db

# Database settings - mysql (prod)
#SASKATOON_DB_ENGINE=django.db.backends.mysql
#SASKATOON_DB_NAME=saskatoon_prod
#SASKATOON_DB_USER=saskatoon
#SASKATOON_DB_PASSWORD=
#SASKATOON_DB_HOST=127.0.0.1

# Misc
SASKATOON_TIME_ZONE=UTC
```

You can optionnaly configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).

To initiate the database use:

```
python3 saskatoon/manage.py migrate --skip-checks
```

ps: in case you have an error similar to this one:

```django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')```

then you'll need to set your database to UTF-8:

```
ALTER DATABASE 'your_saskatoon_database' CHARACTER SET utf8;
```

## Create administrator account

This part is optionnal but you can create a new administrator account to access the admin panel.

This admin panel allow you to see all data of the DB and make some action on it.

To create a new administrator account use :
```
python3 saskatoon/manage.py createsuperuser
```

To access the admin panel go on :
```
localhost:8000/admin
```

## Launch the server

You can use Django embedded server for development purpose:

```
python3 saskatoon/manage.py runserver 8000
```

## Running tests

Tests will look for the config file `test.env`. This minimal configuration us required to run tests:

```
SASKATOON_URL=http://localhost:8000
SASKATOON_EMAIL=admin@just-testing.org
SASKATOON_PASSWORD=password1234
SASKATOON_DB_ENGINE=django.db.backends.sqlite3
SASKATOON_DB_NAME=/YOURPATH/sqlite3-testing.db
```

Tests are located inside `saskatoon/tests` folder. 

Run tests with:

```
tox -e test
```
