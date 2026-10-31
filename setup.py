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
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django :: 5.2",
    ],
    python_requires=">=3.11",
    license="GNU AFFERO GENERAL PUBLIC LICENSE",
    long_description=pathlib.Path(__file__).parent.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=["saskatoon"],
    install_requires=[
        "asgiref>=3.8,<4",
        "cffi>=1.17,<3",
        "crispy-bootstrap4>=2026.2",
        "cryptography>=44,<51",
        "cssbeautifier",
        "Django>=5.2,<5.3",
        "djangorestframework>=3.18,<4",
        "django-autocomplete-light>=5.0,<6",
        "django-filter>=25.2,<26",
        "django-crequest>=2018.5.11,<2019",
        "django-debug-toolbar>=8.0,<9",
        "django-extensions>=4.1,<5",
        "django-geojson>=4.2,<5",
        "django-leaflet>=0.34",
        "mysqlclient>=2.2.1",
        "Pillow>=12.0,<14",
        "pycparser>=2.20,<3",
        "sqlparse>=0.5,<1",
        "django-dotenv>=1.4.2,<2",
        "django-crispy-forms>=2.7,<3",
        "django-rosetta>=0.10.3,<1",
        "django-sortedm2m>=4.0",
        "django-phone-field>=1.8.1,<2",
        "postalcodes-ca>=0.0.9,<1",
        "django-quill-editor>=0.1.42,<1",
        "deal>=4,<5",
        "django-stubs[compatible-mypy]>=5.2,<5.3",
        "django-stubs-ext>=5.2,<5.3",
        "djangorestframework-stubs[compatible-mypy]>=3.16,<3.17",
        "types-setuptools>=81,<82",
        # deal 4.x still relies on typeguard 3 APIs (typeguard.CallMemo)
        "typeguard>=3.0.2,<4",
        "types-django-filter>=25.2,<26",
        "chardet>=3.0.2,<6",
        "geopy",
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
            'djlint',
        ]
    },
)
