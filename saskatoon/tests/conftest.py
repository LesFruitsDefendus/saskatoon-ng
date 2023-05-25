import os
import pytest
import selenium.webdriver
from django.conf import settings

# Load the environment variables from .env file.
import saskatoon.settings

from tests import PAGE_LOAD_TIMEOUT

TESTDRIVER = os.getenv('SASKATOON_TEST_WEBDRIVER')
# A list of selenium webdrivers for different browsers:
# https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference

# From https://pybit.es/selenium-pytest-and-django.html
# Not used right now.
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': os.getenv('SASKATOON_DB_ENGINE'),
        'NAME': os.getenv('SASKATOON_DB_NAME'),
        'USER': os.getenv('SASKATOON_DB_USER'),
        'PASSWORD': os.getenv('SASKATOON_DB_PASSWORD'),
        'HOST': os.getenv('SASKATOON_DB_HOST'),
    }

def create_driver():
    # The webdriver class is instantiated dynamically
    assert TESTDRIVER is not None, ".env variable SASKATOON_TEST_WEBDRIVER not defined, please set the webdriver. i.e. 'Chrome' or 'Firefox'"
    assert hasattr(selenium.webdriver, TESTDRIVER), f"unknown driver value '{TESTDRIVER}' in .env variable SASKATOON_TEST_WEBDRIVER config. Please set a valid webdriver. i.e. 'Chrome' or 'Firefox'"
    
    # Create new driver
    testdriver = getattr(selenium.webdriver, TESTDRIVER)()
    testdriver.implicitly_wait(PAGE_LOAD_TIMEOUT)

    return testdriver

@pytest.fixture(scope="module")
def driver():
    
    testdriver = create_driver()
    yield testdriver
    testdriver.quit()
