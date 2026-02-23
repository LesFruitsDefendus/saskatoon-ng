#! /usr/bin/env python3
from setuptools import setup
import pathlib

# To install basic requirements: (venv)$ pip3 install .
# To install 'test' extra packages: (venv)$ pip3 install 'Saskatoon[test]'

setup(
    name="Saskatoon",
    description="Saskatoon - harverst management system",
    url="https://github.com/LesFruitsDefendus/saskatoon-ng",
    maintainer="Les Fruits Défendus",
    author="Tassia Camoes Araujo, Tiago Bortoletto Vaz, Tristan Landes-Tremblay",
    version="2.dev0",
    classifiers=["Programming Language :: Python :: 3"],
    license="GNU AFFERO GENERAL PUBLIC LICENSE",
    long_description=pathlib.Path(__file__).parent.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=["saskatoon"],
    install_requires=[
        "asgiref>=3.2.7,<4",
        "cffi>=1.14.0,<2",
        "crispy-bootstrap4>=2022.1,<2024",
        "cryptography>=3.3.2,<45",
        "Django>=4.0.0,<5",
        "djangorestframework>=3.11.0,<4",
        "django-autocomplete-light>=3.8.2,<4",
        "django-select2>=8.0,<9",
        "django-filter>=25.0,<26",
        "django-crequest>=2018.5.11,<2019",
        "django-debug-toolbar>=6.0,<7",
        "django-extensions>=4.0,<5",
        "django-geojson>=4.0.0,<5",
        "mysqlclient>=1.4.6",
        "Pillow>=11.0,<12",
        "pycparser>=2.20,<3",
        "sqlparse>=0.3.1,<1",
        "django-dotenv>=1.4.2,<2",
        "django-crispy-forms>=2.0,<3",
        "django-rosetta>=0.9.8,<1",
        "django-phone-field>=1.8.1,<2",
        "postalcodes-ca>=0.0.9,<1",
        "django-quill-editor>=0.1.40,<1",
        "deal[all]>=4,<5",
        "django-stubs[compatible-mypy]>=5,<6",
        "django-stubs-ext>=5,<6",
        "djangorestframework-stubs[compatible-mypy]>=3,<4",
        "types-setuptools>=81,<82",
        "typeguard>=3.0.2,<4",
        "types-django-filter>=25,<26",
        "chardet>=3.0.2,<6",
    ],
    extras_require={
        'test': [
            'invoke',
            'pytest',
            'pytest-django',
            'selenium',
            'tox',
            'hypothesis',
            'ruff',
        ]
    },
)
