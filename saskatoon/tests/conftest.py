import os
import pytest
import selenium.webdriver
from django.conf import settings

# Load the environment variables from .env file.
import saskatoon.settings

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

@pytest.fixture(scope="module")
def driver():
    # The webdriver class is instantiated dynamically
    assert TESTDRIVER is not None, ".env variable SASKATOON_TEST_WEBDRIVER not defined, please set the webdriver. i.e. 'Chrome' or 'Firefox'"
    assert hasattr(selenium.webdriver, TESTDRIVER), f"unknown driver value '{TESTDRIVER}' in .env variable SASKATOON_TEST_WEBDRIVER config. Please set a valid webdriver. i.e. 'Chrome' or 'Firefox'"
    # Create new driver
    if TESTDRIVER == 'Chrome':

        options = selenium.webdriver.ChromeOptions()
        if os.getenv('GITHUB_ACTIONS') == 'true':
            options.binary_location = '/usr/bin/google-chrome'
        testdriver = selenium.webdriver.Chrome(options=options)

    else:
        # Untested!
        testdriver = getattr(selenium.webdriver, TESTDRIVER)()
    
    yield testdriver
    testdriver.quit()
