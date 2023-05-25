
# Django checks

Run

```
./saskatoon/manage.py check --database default
./saskatoon/manage.py validate_templates
```

# Selenium-driven tests

## pytest

## requirements

See *setup.py* for requirements:
```
$(venv) pip3 install 'Saskatoon[test]'
```

## WebDriver

[A list of selenium webdrivers for different browsers](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference)

E.g. to install Chrome Webdriver:
- get the latest release [here](https://chromedriver.storage.googleapis.com/index.html)
- unzip the package into an appropriate directory
- make sure this directory belongs to ~$PATH~

**WARNING**: at the moment only the Chrome WebDriver works. Using ~webdriver.Firefox~ I consistently get the error `E: selenium.common.exceptions.TimeoutException: Message: Can't locate login form` when trying to log in through ~tests.helpers.login()~


## To run tests manually

- start a local server :`$(venv) python3 saskatoon/manage.py runserver 8000`
- run a single test: `$ (venv) python3 -m pytest saskatoon/test/test_urls.py`
- run all tests (as defined in *pytest.ini*): `$(venv) python3 -m pytest -s`

NB: the `-s` flag is used to allow debug prints to show in the output.

## runtests.sh

This script starts a local server in the background and run all tests, 
no need to setup extra test config, the script does it automatically.

```
$(venv) saskatoon/tests/runtests.sh
```

## To run all tests using tox

This is basically the same as running ``runtests.sh``.

```
$(venv) tox -e
```
