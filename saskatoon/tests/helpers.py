import os
# from selenium import webdriver
from .conftest import testdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from . import PAGE_LOAD_TIMEOUT

def login(driver: testdriver) -> None:
    """
    Helper method to authenticate a driver.
    """
    # Manually login into Saskatoon

    # TODO: README.md
    saskatoon_url = os.getenv('SASKATOON_URL')
    saskatoon_email = os.getenv('SASKATOON_ADMIN_EMAIL')
    saskatoon_pass = os.getenv('SASKATOON_ADMIN_PASSWORD')

    driver.get(saskatoon_url+"/accounts/login/?next=/")

    # Wait for the login form to show up
    #                                                                           HTML TAG
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#l-login > form > div.nk-form > button")), "Can't locate login form")

    # Fill username / password
    driver.find_element_by_id("id_username").send_keys(saskatoon_email)
    driver.find_element_by_id ("id_password").send_keys(saskatoon_pass)

    # Click on login button
    driver.find_element_by_css_selector("#l-login > form > div.nk-form > button").click()

    try: WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.visibility_of_element_located ((By.CLASS_NAME, "main-menu-area")), "Can't locate main menu")
    except Exception as e:
        # We are still at the login page
        if '/accounts/login/' in driver.current_url:
            raise RuntimeError("Login failed") from e
        else: raise

def logoff(driver: testdriver) -> None:
    """
    Helper method to logoff a driver.
    """
    # Click on user icon
    driver.find_element_by_css_selector("body > div.header-top-area > div > div > div.col-lg-4.col-md-4.col-sm-12.col-xs-12 > div > ul > li:nth-child(1) > a").click()
    logoff_selector = "body > div.header-top-area > div > div > div.col-lg-4.col-md-4.col-sm-12.col-xs-12 > div > ul > li.nav-item.dropdown.open > ul > li:nth-child(2) > a"
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, logoff_selector)), "Can't locate logoff button")
    # then click on logoff
    driver.find_element_by_css_selector(logoff_selector).click()
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#content > p:nth-child(3) > a")), "Can't locate django admin panel 'Log in again' button.")
