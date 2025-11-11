import os
from selenium.webdriver import Remote
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from . import PAGE_LOAD_TIMEOUT
from .helpers import login, logoff


URLS = [
    '/harvest/',
    '/property/',
    '/organization/',
    '/community/',
    '/property/create_public/',
    '/calendar',
]

PUBLIC_URLS = [
    '/property/create_public/',
    '/calendar',
]


def test_urls(driver: Remote) -> None:
    driver.implicitly_wait(PAGE_LOAD_TIMEOUT)

    def test_url(url, needs_auth):
        print(f"\r\ntesting url: {url}")
        if needs_auth:
            login(driver)

        testurl = os.getenv('SASKATOON_URL') + url
        driver.get(testurl)

        className = "main-menu-area" if needs_auth else "footer-copyright-area"
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, className)),
            f"Can't locate {className} on page {url}",
        )
        assert url in driver.current_url
        assert 'html' in driver.page_source
        if needs_auth:
            logoff(driver)

    for url in URLS:
        test_url(url, True)

    for url in PUBLIC_URLS:
        test_url(url, False)
