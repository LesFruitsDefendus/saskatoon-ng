import os
import sys
from pathlib import Path
import pytest
from django.conf import settings
from selenium import webdriver

from dotenv import load_dotenv, find_dotenv #type: ignore

# Appending saskatoon project to the python PATH for testing
# sys.path.append(Path(__file__).parent.as_posix())

# pytest_plugins = ("pytest_django",)

# Load the environment variables from .env file. 
file = find_dotenv(filename='test.env', raise_error_if_not_found=True,)
if file:
    load_dotenv(dotenv_path=file)

# From https://pybit.es/selenium-pytest-and-django.html

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': os.getenv('SASKATOON_DB_ENGINE'),
        'NAME': os.getenv('SASKATOON_DB_NAME'),
        'USER': os.getenv('SASKATOON_DB_USER'),
        'PASSWORD': os.getenv('SASKATOON_DB_PASSWORD'),
        'HOST': os.getenv('SASKATOON_DB_HOST'),
    }

@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    return driver

