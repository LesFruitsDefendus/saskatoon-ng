# Installation guide

Please follow each part of this documentation to install the project.

## Installation of requirements

- MySQL client

    For Ubuntu: 
    ```
    apt-get install libmysqlclient-dev
    ```

    For MacOS:
    ```
    brew install mysql-client
    echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

- Pillow requirements
    For Ubuntu: 
    ```
    sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev
    ```

    For MacOS:
    ```
    brew install libtiff libjpeg webp little-cms2 zlib
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
pip install -r requirements.txt
```

## Database

We use an `sqlite3` database in our development environment because it's really fast to setup.

You can optionnaly configure other database engines. Please refer to [this Django documentation](https://docs.djangoproject.com/en/3.2/ref/settings/#databases).

The setting file is provided as `saskatoon/saskatoon/settings.py`. Edit `DATABASES` entry to use an `sqlite3` database: 
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/Users/me/Documents/saskatoon-dev/sqlite3.db',
    }
}
```

To initiate the database use: (NOT WOKRING AT THE MOMENT, are we missing migration files ?)
```
cd saskatoon
python3 manage.py migrate
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

Django have an embedded server for development purpose. To run the development server use :

```
cd saskatoon
python3 manage.py runserver 8000
```
