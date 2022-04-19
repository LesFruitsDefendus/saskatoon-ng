import os
import time
from typing import Any, List, Optional
import attr

from selenium.webdriver import Remote
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC, select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests import PAGE_LOAD_TIMEOUT

def assert_not_error_page(driver: Remote) -> None:
    try:
        summary = driver.find_element(By.ID, 'summary')
        info = driver.find_element(By.ID, 'info')
    except NoSuchElementException:
        return
    else:
        raise AssertionError(f"Error on page {driver.current_url}: {summary.get_attribute('innerHTML')}")

def login(driver: Remote) -> None:
    """
    Helper method to authenticate a driver.
    """

    # TODO: README.md
    saskatoon_url = os.getenv('SASKATOON_URL')
    saskatoon_email = os.getenv('SASKATOON_ADMIN_EMAIL')
    saskatoon_pass = os.getenv('SASKATOON_ADMIN_PASSWORD')

    assert saskatoon_email is not None
    assert saskatoon_pass is not None

    driver.get(saskatoon_url+"/accounts/login/?next=/")

    # Wait for the login form to show up
    #                                                                           HTML TAG
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#l-login > form > div.nk-form > button")), "Can't locate login form")

    # Fill username / password
    driver.find_element(By.ID, "id_username").send_keys(saskatoon_email)
    driver.find_element(By.ID, "id_password").send_keys(saskatoon_pass)

    # Click on login button
    time.sleep(0.25)
    driver.find_element(By.CSS_SELECTOR, "#l-login > form > div.nk-form > button").click()

    try: WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.visibility_of_element_located ((By.CLASS_NAME, "main-menu-area")), "Can't locate main menu")
    except Exception as e:
        # We are still at the login page
        if '/accounts/login/' in driver.current_url:
            raise RuntimeError("Login failed") from e
        else: raise

def logoff(driver: Remote) -> None:
    """
    Helper method to logoff a driver.
    """
    
    user_icon_selector = "li.nav-item:nth-child(1) > a:nth-child(1)"
    logoff_selector = "li.nav-item:nth-child(1) > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)"
    login_selector = ".nav > li:nth-child(1) > a:nth-child(1)"

    # Click on user icon
    driver.find_element(By.CSS_SELECTOR, user_icon_selector).click()
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, logoff_selector)), "Can't locate logoff button")
    # then click on logoff
    driver.find_element(By.CSS_SELECTOR, logoff_selector).click()
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_selector)), "Can't locate login button.")

@attr.s(auto_attribs=True)
class SaskatoonFormFiller:
    """
    Try to be smart about forms...
    """
    driver: Remote

    def fill(self, input_type:str, css_selector:str, value:Any) -> None:
        method = 'fill_' + input_type
        getattr(self, method)(css_selector, value)
       
    def fill_nullbooleanselect(self, css_selector, value: Optional[bool]):
        if value == None:
            v = 'unknown'
        elif value == True:
            v = 'true'
        else:
            v = 'false'
        # https://stackoverflow.com/a/32382542
        input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        input_element.click()
        s = select.Select(input_element)
        s.select_by_value(v)
    
    def fill_checkboxinput(self, css_selector, value:bool):
        input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        if value and not input_element.is_selected():
            input_element.click()
    
    def fill_multipleselection(self, css_selector, value: List):
        for v in value:
            input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector + ' input')
            input_element.send_keys(v)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 
                    f'#select2-{css_selector[5:]}-results > li.select2-results__option--highlighted')), 
                f"Can't find your choice {value}")
            time.sleep(0.5)
            input_element.send_keys(Keys.ENTER)
            time.sleep(0.5)

    def fill_textinput(self, css_selector, value: str):
        input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        input_element.send_keys(value)

    def fill_numberinput(self, css_selector, value: str):
        input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        input_element.send_keys(Keys.CONTROL, 'a')
        input_element.send_keys(Keys.DELETE)
        input_element.send_keys(value)

    def fill_dateinput(self, css_selector, value: str):
        input_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        input_element.send_keys(value)

    def fill_singleselection(self, css_selector:str, value: str):
        select_element = self.driver.find_element(By.CSS_SELECTOR, css_selector + ' .select2-container')
        select_element.click()

        in_select = f"input[aria-controls=select2-{css_selector[5:]}-results]"
        input_element = self.driver.find_element(By.CSS_SELECTOR, in_select)
        input_element.send_keys(value)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 
                f'#select2-{css_selector[5:]}-results > li.select2-results__option--highlighted')), 
            f"Can't find your choice {value}")
        time.sleep(1)
        input_element.send_keys(Keys.ENTER)

    def fill_select(self, css_selector, value: str):
        select_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        s = select.Select(select_element)
        s.select_by_value(value)
