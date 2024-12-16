# Testing Guide

## Overview
1. [Requirements](#requirements)
2. [Django checks](#django-checks)
3. [Unit tests](#unit-tests)
4. [Selenium tests](#selenium-driven-tests)
5. [Testing with tox](#testing-with-tox)

## Requirements

Install Saskatoon test dependencies in the virtual environment:

```
(venv)$ pip3 install '.[test]'
```

See `setup.py` for more details on the project's package requirements

## Django checks

There are a few basic checks to help validate the Django projects during development.

### Database checks

```
(venv)$ ./saskatoon/manage.py check --database default
```

See more in [Django docs on check command](https://docs.djangoproject.com/en/3.2/ref/django-admin/#check).

### Template validation

```
(venv)$ ./saskatoon/manage.py validate_templates
```

This command only checks for Django template syntax errors by trying to load templates using Django's template loader. It does not validate HTML. 

## Unit tests

- To run a single test suite: `(venv)$ python3 -m pytest saskatoon/unittests/test_permission.py`
- To run all tests: `(venv)$ python3 -m pytest saskatoon/unittests -s` _(the `-s` flag allows debug info to show in the output.)_

## Selenium-driven tests

[Selenium](https://www.selenium.dev/) is a browser-based testing tool. It mimics end-user operations on a browser to test the Django project at runtime.

> WARNING: At the moment only the Chrome WebDriver works, and thus all settings/debugging here are based on Chrome.
>
> _Using ~webdriver.Firefox~ I consistently get the error `E: selenium.common.exceptions.TimeoutException: Message: Can't locate login form` when trying to log in through ~tests.helpers.login()~_

### Configuration

#### .env settings

Add/enable these lines in the ``saskatoon/.env`` file:

```
SASKATOON_TEST_WEBDRIVER=Chrome
SASKATOON_URL=http://127.0.0.1:8000
SASKATOON_ADMIN_EMAIL=admin@example.com
SASKATOON_ADMIN_PASSWORD=testing1234
```

#### Create test superuser

```
(venv)$ python3 saskatoon/tests/createtestsuperuser.py admin@example.com testing1234
```

#### WebDriver related issues

Selenium may not properly install web drivers during its installation. If you get an "unable to locate driver" error, you may fix it by manually install the web driver and add it to $PATH (See more at [Selenium docs](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference)).

To install Chrome Webdriver:
1. Get the latest release compatible with your system.
    - [ChromeDriver version 115 and above](https://googlechromelabs.github.io/chrome-for-testing/)
    - [ChromeDriver version 114 and below](https://chromedriver.storage.googleapis.com/index.html)
2. Unzip the package into an appropriate directory.
3. Add this directory to ~$PATH~:
    ```
    echo 'export PATH=$PATH:/path/to/driver' >> ~/.zshenv
    source ~/.zshenv
    ```
4. Test if it has been added correctly by checking the version of the driver:
    ```
    chromedriver --version
    ```
If after this you get another "unable to obtain chrome driver" error, run this command to debug:
```
/venv/lib/python3.9/site-packages/selenium/webdriver/common/macos/selenium-manager --browser chrome --output json
```
If you get an error like `dyld: cannot load 'selenium-manager' (load command 0x80000034 is unknown)`, it could be your system is incompatible with the latest Selenium, and may be fixed by downgrade Selenium to version 4.20.0 (see more in [this post](https://github.com/SeleniumHQ/selenium/issues/13974)).

### Run tests

#### Manually

First, start a local server with `(venv)$ python3 saskatoon/manage.py runserver 8000`.

- To run a single test suite: `(venv)$ python3 -m pytest saskatoon/tests/test_urls.py`
- To run all tests (as defined in *pytest.ini*): `(venv)$ python3 -m pytest -s` _(the `-s` flag allows debug info to show in the output.)_

#### Automatically with runtests.sh

This script starts a local server in the background and run all tests:
```
(venv)$ saskatoon/tests/runtests.sh
```

## Testing with tox

[Tox](https://tox.wiki/) is a test automation tool. Both Django checks and Selenium-driven tests can be run via tox:

- To run Django checks: `(venv)$ tox -e checks`
- To run unit tests: `(venv)$ tox -e unittests`
- To run selenium-driven tests: `(venv)$ tox -e test`

See [tox.ini](../../tox.ini) for more details and other tests.
