import os
import time

from selenium.webdriver import Remote
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from . import PAGE_LOAD_TIMEOUT


def login(driver: Remote) -> None:
    """
    Helper method to authenticate a driver.
    """
    # Manually login into Saskatoon
    driver.implicitly_wait(PAGE_LOAD_TIMEOUT)

    # TODO: README.md
    saskatoon_url = os.environ['SASKATOON_URL']
    saskatoon_email = os.environ['SASKATOON_ADMIN_EMAIL']
    saskatoon_pass = os.environ['SASKATOON_ADMIN_PASSWORD']

    driver.get(saskatoon_url + "/accounts/login/?next=/")

    # Wait for the login form to show up
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#l-login > form > div.nk-form > button")),
        "Can't locate login form",
    )

    # Fill username / password
    driver.find_element(By.ID, "id_username").send_keys(saskatoon_email)
    driver.find_element(By.ID, "id_password").send_keys(saskatoon_pass)

    # Click on login button
    time.sleep(0.25)
    driver.find_element(By.CSS_SELECTOR, "#l-login > form > div.nk-form > button").click()

    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "main-menu-area")),
            "Can't locate main menu",
        )
    except Exception as e:
        # We are still at the login page
        if '/accounts/login/' in driver.current_url:
            raise RuntimeError("Login failed") from e
        else:
            raise


def logoff(driver: Remote) -> None:
    """
    Helper method to logoff a driver.
    """

    user_icon_selector = "li.nav-item:nth-child(1) > a:nth-child(1)"
    logoff_selector = (
        "li.nav-item:nth-child(1) > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)"  # noqa E501
    )
    login_selector = ".nav > li:nth-child(1) > a:nth-child(1)"

    # Click on user icon
    driver.find_element(By.CSS_SELECTOR, user_icon_selector).click()
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, logoff_selector)),
        "Can't locate logoff button",
    )
    # then click on logoff
    driver.find_element(By.CSS_SELECTOR, logoff_selector).click()
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, login_selector)),
        "Can't locate login button.",
    )
