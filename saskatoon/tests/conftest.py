import os
import pytest
import selenium.webdriver
from django.conf import settings
from dotenv import read_dotenv
from saskatoon.settings import dotenv

# Load the environment variables from .env file.
read_dotenv(dotenv=dotenv)

TESTDRIVER = os.getenv('SASKATOON_TEST_WEBDRIVER')


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Not used at the moment.
    From: https://pybit.es/selenium-pytest-and-django.html
    """

    settings.DATABASES['default'] = {
        'ENGINE': os.getenv('SASKATOON_DB_ENGINE'),
        'NAME': os.getenv('SASKATOON_DB_NAME'),
        'USER': os.getenv('SASKATOON_DB_USER'),
        'PASSWORD': os.getenv('SASKATOON_DB_PASSWORD'),
        'HOST': os.getenv('SASKATOON_DB_HOST'),
    }


@pytest.fixture(scope="module")
def driver():
    # The webdriver class is instantiated dynamically
    assert TESTDRIVER is not None, (
        ".env variable SASKATOON_TEST_WEBDRIVER not defined, \
please set the webdriver. i.e. 'Chrome' or 'Firefox'"
    )

    assert hasattr(selenium.webdriver, TESTDRIVER), (
        f"unknown driver value '{TESTDRIVER}' in .env \
variable SASKATOON_TEST_WEBDRIVER config. Please set a valid webdriver. i.e. 'Chrome' or 'Firefox'"
    )

    # Create new driver
    testdriver = getattr(selenium.webdriver, TESTDRIVER)()
    yield testdriver
    testdriver.quit()
