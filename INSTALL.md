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
pip3 install -r requirements.txt
```

## Database

Edit the DB path file at `saskatoon/saskatoon/settings.py`, section `DATABASES`:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/YOURDBPATH/sqlite3.db',
    }
}
```
You can optionnaly configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).

To initiate the database use:

```
cd saskatoon
python3 manage.py migrate --skip-checks
```

## Create administrator account

This part is optionnal but you can create a new administrator account to access the admin panel.

This admin panel allow you to see all data of the DB and make some action on it.

To create a new administrator account use :
```
cd saskatoon
python3 manage.py createsuperuser
```

To access the admin panel go on :
```
localhost:8000/admin
```

## Launch the server

You can use Django embedded server for development purpose:

```
cd saskatoon
python3 manage.py runserver 8000
```
