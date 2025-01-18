import os
from selenium.webdriver import Remote

def test_login_logoff(driver: Remote) -> None:
    pass

def test_reset_password(driver: Remote) -> None:
    pass

def test_add_property(driver: Remote) -> None:
    pass

def test_add_harvest(driver: Remote) -> None:
    driver.get(os.getenv('SASKATOON_URL')+'/harvest/create')

    "#id_status > option:nth-child(2)"

def test_add_beneficiary(driver: Remote) -> None:
    pass
