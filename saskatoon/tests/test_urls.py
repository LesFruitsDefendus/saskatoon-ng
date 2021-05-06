import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from . import PAGE_LOAD_TIMEOUT
from .helpers import login, logoff

# List of (url, expected_html_body_parts, needs_auth)
# TODO: List all static pages. 
urls = [
    ('/harvest/', ['html'], True),
    ('/property/', ['html'], True),
    ('/beneficiary/', ['html'], True),
    ('/community/', ['html'], True),
    ('/property/create_public', ['html'], False),
    ('/calendar', ['html'], False),
]

def test_urls(driver: webdriver.Chrome) -> None:
    driver.implicitly_wait(PAGE_LOAD_TIMEOUT)

    def test_url(url_part, expected_html_body_parts):
        
        driver.get(os.getenv('SASKATOON_URL') + url_part)
        
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.visibility_of_all_elements_located((By.CLASS_NAME,  "footer-copyright-area")), f"Can't locate footer on page {url_part}")
        
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
                logoff(driver)
            else:
                raise
        else:
            if needs_auth:
                raise RuntimeError(f"Security Alert: The private page {url_part} is accessible without beeing logged in!")
        