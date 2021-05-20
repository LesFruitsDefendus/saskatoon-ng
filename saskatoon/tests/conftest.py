import os
import pytest
from django.conf import settings

from dotenv import load_dotenv, find_dotenv #type: ignore

# Load the environment variables from .env file.
file = find_dotenv()
if file: load_dotenv(dotenv_path=file)

TESTDRIVER = os.getenv('SASKATOON_TEST_WEBDRIVER')
# A list of selenium webdrivers for different browsers:
# https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference

#TODO add more options if needed
if TESTDRIVER == 'Firefox':
    # WARNING: Firefox doesn't work for now
    from selenium.webdriver import Firefox
    testdriver = Firefox()
elif TESTDRIVER == 'Chrome':
    from selenium.webdriver import Chrome
    testdriver = Chrome()
else:
    testdriver = None
    print('WARNING: .env variable SASKATOON_TEST_WEBDRIVER not defined or unknown')

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
    driver = testdriver
    yield driver
    driver.quit()
