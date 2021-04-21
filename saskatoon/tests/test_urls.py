import pytest
import os
from selenium import webdriver

from .conftest import login

# List of (url, expected_html_body_parts, needs_auth)
urls = [
    ('/calendar', [''], False),
    ('/harvest', [''], True),
    ('/property', [''], True),
    ('/equipment', [''], True),
    ('/beneficiary', [''], True),
    ('/community', [''], True),
    ('/participation', [''], True),
]

def test_urls(driver: webdriver.Chrome) -> None:
    for url_part, expected_html_body_parts, needs_auth in urls:
        if needs_auth:
            driver = login(driver)
        driver.get(os.getenv('SASKATOON_URL') + url_part)
        for part in expected_html_body_parts:
            assert part in driver.page_source
