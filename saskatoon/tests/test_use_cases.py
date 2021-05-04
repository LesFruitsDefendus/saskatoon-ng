import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .helpers import login

def test_login_logoff(driver: webdriver.Chrome) -> None:
    pass

def test_reset_password(driver: webdriver.Chrome) -> None:
    pass

def test_add_property(driver: webdriver.Chrome) -> None:
    pass

def test_add_harvest(driver: webdriver.Chrome) -> None:
    pass
    # driver.get(os.getenv('SASKATOON_URL')+'/harvest/create')
    

def test_add_beneficiary(driver: webdriver.Chrome) -> None:
    pass
