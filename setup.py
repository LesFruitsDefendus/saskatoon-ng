#! /usr/bin/env python3
from setuptools import setup, find_packages
import pathlib

# To install basic requirements: (venv)$ pip3 install .
# To install 'test' extra packages: (venv)$ pip3 install 'Saskatoon[test]'

setup(
    name                =   "Saskatoon",
    description         =   "Saskatoon - harverst management system",
    url                 =   "https://github.com/LesFruitsDefendus/saskatoon-ng",
    maintainer          =   "Les Fruits Défendus",
    author              =   "Tassia Camoes Araujo, Tiago Bortoletto Vaz, Tristan Landes-Tremblay",
    version             =   "2.dev0",
    classifiers         =   ["Programming Language :: Python :: 3"],
    license             =   "GNU AFFERO GENERAL PUBLIC LICENSE",
    long_description    =   pathlib.Path(__file__).parent.joinpath("README.md").read_text(),
    long_description_content_type   =   "text/markdown",
    install_requires    =   [
        "asgiref>=3.2.7",
        "cffi>=1.14.0",
        "cryptography>=3.3.2",
        "Django>=3.0.14,<4.0.0",
        "django-geojson==3.0.0",
        "django-leaflet==0.26.0",
        "django-rest-knox==4.1.0",
        "djangorestframework>=3.11.0",
        "django-autocomplete-light>=3.8.2",
        "django-select2",
        "django-ckeditor",
        "django-filter",
        "django-crequest",
        "django-debug-toolbar",
        "django-extensions",
        "jsonfield==3.1.0",
        "mysqlclient==1.4.6",
        "Pillow==8.3.2",
        "pycparser==2.20",
        "pytz==2020.1",
        "six==1.15.0",
        "sqlparse==0.3.1",
        "django-redis",
        "django-dotenv",
        "django-crispy-forms",
        "django-rosetta==0.9.8"
    ],
    extras_require      =   {
        'test': ['pytest', 'selenium', 'pytest-django', 'invoke', 'tox']
    },
)
