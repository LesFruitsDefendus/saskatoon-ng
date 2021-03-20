#! /usr/bin/env python3
from setuptools import setup, find_packages

# The directory containing this file
import pathlib
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

REQUIREMENTS = [
    "asgiref==3.2.7",
    "cffi==1.14.0",
    "cryptography==3.3.2",
    "Django==3.0.7",
    "django-geojson==3.0.0",
    "django-leaflet==0.26.0",
    "django-rest-knox==4.1.0",
    "djangorestframework==3.11.0",
    "django-autocomplete-light",
    "django-select2",
    "django-ckeditor",
    "django-filter",
    "django-bootstrap3",
    "django-bootstrap-form",
    "django-crequest",
    "jsonfield==3.1.0",
    "mysqlclient==1.4.6",
    "Pillow==7.1.2",
    "pycparser==2.20",
    "pytz==2020.1",
    "six==1.15.0",
    "sqlparse==0.3.1",
]

setup(
    name                =   "Saskatoon",
    description         =   "The new generation Saskatoon harverst management system",
    url                 =   "https://github.com/LesFruitsDefendus/saskatoon-ng",
    maintainer          =   "Les Fruits Défendus",
    author              =   "Tiago Vaz",
    version             =   "2.dev0",
    classifiers         =   ["Programming Language :: Python :: 3"],
    license             =   "GNU AFFERO GENERAL PUBLIC LICENSE",
    long_description    =   README,
    long_description_content_type   =   "text/markdown",
    install_requires    =   REQUIREMENTS,
)
