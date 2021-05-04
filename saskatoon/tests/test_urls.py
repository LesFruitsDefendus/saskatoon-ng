import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .helpers import login

# List of (url, expected_html_body_parts, needs_auth)
# TODO
urls = [
    ('/harvest/', ['html'], True),
    ('/property/', ['html'], True),
    ('/beneficiary/', ['html'], True),
    ('/community/', ['html'], True),
    ('/property/create_public', ['html'], False),
]

def test_urls(driver: webdriver.Chrome) -> None:

    def test_url(url_part, expected_html_body_parts):
        driver.get(os.getenv('SASKATOON_URL') + url_part)
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located ((By.CLASS_NAME, "main-menu-area")), "Can't locate main menu")
        
        assert url_part in driver.current_url

        for part in expected_html_body_parts:
            assert part in driver.page_source

    for url_part, expected_html_body_parts, needs_auth in urls:

        try:
            test_url(url_part, expected_html_body_parts)
        except (AssertionError, TimeoutException):
            if needs_auth:
                login(driver)
                test_url(url_part, expected_html_body_parts)
            else:
                raise
        