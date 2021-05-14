# Local Installation guide

Please follow each part of this documentation in order to run your own instance of Saskatoon.

## Requirements

1. MySQL client

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

2. Python virtualenv

    To install Python requirements in a virtual environment:
    ```
    $ sudo apt install python3-dev
    $ pip3 install virtualenv
    $ virtualenv venv
    $ . venv/bin/activate
    $(venv) pip3 install .
    ```

    See `setup.py` for more details on the project's package requirements

    NB: you might run into issues when installing the `Pillow` package using `pip`, in which case installing the following dependencies should help:

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

Adapt the following `.env` file and place it inside `saskatoon/` project directory.
```
# SECURITY WARNING: keep the secret key used in production secret!
# More infos: https://docs.djangoproject.com/fr/3.1/ref/settings/#secret-key
SASKATOON_SECRET_KEY='<KEY>'

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

NB: to generate a new random secret key, you can run this python script:
```
from django.core.management import utils

print(utils.get_random_secret_key())
```

## local database

1. SQLite

To use a simple *sqlite3.db* database `SASKATOON_DB_ENGINE` must be set to `django.db.backends.sqlite3` in `.env`.

You can optionally configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).


2. MySQL

On Debian and derivatives: (TODO: check)
```
$ sudo apt install mysql-server
$ sudo systemctl start mysql
$ sudo systemctl enable mysql
$ sudo systemctl status mysql
$ sudo mysql_secure_installation
```

To create an empty database:
```
$ mysql -u root -p
> CREATE USER '<user>'@'localhost' IDENTIFIED BY '<password>';
> SELECT user FROM mysql.user;   // show all users
> CREATE DATABASE saskatoon_dev;
> SHOW DATABASES;
> GRANT ALL PRVILEGES ON saskatoon_dev.* TO '<user>'@'localhost';
> ALTER DATABASE saskatoon_dev CHARACTER SET utf8;

```

To import a *.sql* database (dump):
```
TODO
```

Example *.env* file for a local mysql configuration:
```
SASKATOON_SECRET_KEY='<KEY>'
SASKATOON_DEBUG=yes

SASKATOON_DB_ENGINE=django.db.backends.mysql
SASKATOON_DB_NAME=saskatoon_dev
SASKATOON_DB_USER=<user>
SASKATOON_DB_PASSWORD=<password>
SASKATOON_DB_HOST=127.0.0.1

SASKATOON_TIME_ZONE=UTC
```


## Django setup

To initiate the database:
```
$ source venv/bin/activate
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

WARNING: This is not suitable for production use!

TODO: consider [Whitenoise](http://whitenoise.evans.io/en/stable/django.html#django-middleware) for static files handling?


### Launch the server on localhost

You can use Django embedded server for development purpose:
```
python3 saskatoon/manage.py runserver 8000
```

NB: to access the admin panel visit [localhost:8000/admin](http://127.0.0.1:8000/admin)
