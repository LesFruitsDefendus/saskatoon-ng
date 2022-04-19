from pathlib import Path
import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Remote
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC, select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

if __name__ == '__main__':
    import sys
    sys.path.insert(0, Path(__file__).parent.parent.absolute().as_posix())

from tests.helpers import login, SaskatoonFormFiller, assert_not_error_page
from tests.conftest import create_driver

def test_login_logoff(driver: Remote) -> None:
    pass

def test_reset_password(driver: Remote) -> None:
    pass

def test_add_property(driver: Remote) -> None:
    login(driver)

    driver.get(os.getenv('SASKATOON_URL')+'/property/create/')

    assert 'Nice Owner at 4080 Mont Royal' not in driver.page_source, "Property 'Nice Owner at 4080 Mont Royal' already exists, tests must be run on a fresh database."

    ff = SaskatoonFormFiller(driver)

    ff.fill('checkboxinput', '#id_is_active', True)
    ff.fill('nullbooleanselect', '#id_authorized', True)
    ff.fill('multipleselection', '#div_id_trees', ['Amélanc', 'Pommier v'])
    ff.fill('textinput', '#id_trees_location', 'Jardin')
    ff.fill('numberinput', '#id_avg_nb_required_pickers', '3')
    ff.fill('textinput', '#id_trees_accessibility', 'The tree is in the back yard, accessible from the ally')
    ff.fill('checkboxinput', '#id_public_access', True)
    ff.fill('checkboxinput', '#id_neighbor_access', True)
    ff.fill('checkboxinput', '#id_compost_bin', True)
    ff.fill('checkboxinput', '#id_ladder_available', True)
    ff.fill('checkboxinput', '#id_ladder_available_for_outside_picks', True)
    ff.fill('checkboxinput', '#id_harvest_every_year', True)
    ff.fill('numberinput', '#id_number_of_trees', '2')
    ff.fill('dateinput', '#id_approximative_maturity_date', '2028-08-25')
    ff.fill('numberinput', '#id_fruits_height', '3')
    ff.fill('textinput', '#id_additional_info', 'Owner is very nice')
    ff.fill('checkboxinput', '#id_create_new_owner', False)
    ff.fill('singleselection', '#div_id_owner', 'nice')
    ff.fill('textinput', '#id_street_number', '4080')
    ff.fill('textinput', '#id_street', 'Mont Royal')
    ff.fill('textinput', '#id_complement', 'Apt 3')
    ff.fill('textinput', '#id_postal_code', 'H2S1R6')
    ff.fill('select', '#id_neighborhood', '19')
    ff.fill('select', '#id_city', '1')
    ff.fill('select', '#id_state', '1')
    ff.fill('select', '#id_country', '1')
    ff.fill('textinput', '#id_publishable_location', 'Mont Royal / Saint Laurent')

    driver.find_element(By.CSS_SELECTOR, 'html .form-group form .btn-primary').click()
    assert_not_error_page(driver)
    
    driver.get(os.getenv('SASKATOON_URL')+'/property/')

    # FIXME: Currently it seems that the standard new property form does not associate the property owner with the property
    # in one go, we nee to go back to the edit page and re-associate the owner to the property.
    if True:
        # click on the last added property
        driver.find_element(By.CSS_SELECTOR, 'tr.odd:nth-child(1) > td:nth-child(2) > a:nth-child(1)').click()
        property_update_url = f"{driver.current_url[:-3]}/update/{driver.current_url[-2:]}"
        # goto the edit page of thi property
        driver.get(property_update_url)
        assert_not_error_page(driver)
        ff.fill('singleselection', '#div_id_owner', 'nice')
        driver.find_element(By.CSS_SELECTOR, 'html .form-group form .btn-primary').click()
        assert_not_error_page(driver)
        driver.get(os.getenv('SASKATOON_URL')+'/property/')

    assert driver.find_element(By.CSS_SELECTOR, 
        'tr:nth-child(1) > td:nth-child(2) > a:nth-child(1)').get_attribute(
            'innerHTML') == 'Nice Owner at 4080 Mont Royal'
    
def test_add_harvest(driver: Remote) -> None:
    driver.get(os.getenv('SASKATOON_URL')+'/harvest/create')

    "#id_status > option:nth-child(2)"

def test_add_beneficiary(driver: Remote) -> None:
    pass
