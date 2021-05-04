import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def login(driver: webdriver.Chrome) -> webdriver.Chrome:
    """
    Helper method to authenticate a driver.
    """
    # Manually login into Saskatoon

    saskatoon_url = os.getenv('SASKATOON_URL')
    saskatoon_email = os.getenv('SASKATOON_EMAIL')
    saskatoon_pass = os.getenv('SASKATOON_PASSWORD')

    driver.get(saskatoon_url+"/accounts/login/?next=/")

    # Wait for the login button to be clickable
    #                                                                           HTML TAG
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#id_username")), "Can't locate login form")

    # Fill username / password
    driver.find_element_by_id("id_username").send_keys(saskatoon_email) #                               HTML TAG
    driver.find_element_by_id ("id_password").send_keys(saskatoon_pass) #                              HTML TAG

    # Click on login button
    driver.find_element_by_css_selector("#l-login > form > div.nk-form > button").click() #     HTML TAG

    try: WebDriverWait(driver, 3).until(EC.visibility_of_element_located ((By.CLASS_NAME, "main-menu-area")), "Can't locate main menu")
    except Exception as e:
        if '/accounts/login/' in driver.current_url:
            raise RuntimeError("Login failed") from e
        else: raise

def logoff(driver: webdriver.Chrome) -> webdriver.Chrome:
    """
    """
    # TODO
