# Fixtures

Using fixtures is a quick way to load hard-coded data to Django models (see more in [Django docs](https://docs.djangoproject.com/en/dev/howto/initial-data/)). Saskatoon provides a set of fixtures as sample data for development and testing.

_NOTE: A Redis server must be run in the background while loading fixtures._

## Initialise the database with all fixtures

For the first time, the fixtures need be loaded in a specific sequence, since there are dependencies (see more on database model structure in [Database model docs](../../doc/db-model.pdf)).

To initialise the database:
1. Audit/modify the individual `.json` files located in `saskatoon/fixtures`
2. Run `(venv)$ saskatoon/fixtures/init`

> ### Note 
> If you get `ConnectionRefusedError: [Errno 111] Connection refused` error on `send_mail()` function it means your local mail server is not properly configured. 
> 
> One way to ignore this issue is to keep the `EMAIL_HOST=` variable empty in your `.env` file. (see `saskatoon/harvest/signals.py` for more details)

## Common actions
Here are some common ways to use the `loaddata` and `dumpdata` scripts. 

>  ### Warning
>  Each time you run `loaddata`, the data will be read from the fixture and re-loaded into the database. Note this means that if you change one of the rows created by a fixture and then run `loaddata` again, you’ll wipe out any changes you’ve made.

### Load all .json files located in `saskatoon/fixtures`
```
(venv)$ saskatoon/fixtures/loaddata all
```
Note: this does not include .json files of the type: `saskatoon*.json`

### Load a single app or model instance
```
(venv)$ saskatoon/fixtures/loaddata <instance>
```
For example, running `saskatoon/fixtures/loaddata member-city` will load the `member-city.json` file into the database.

### Export all data from a pre-populated database
```
(venv)$ saskatoon/fixtures/dumpdata
```
This will create `saksatoon/fixtures/saksatoon.json`

### Export data from a specific app or table
```
(venv)$ saskatoon/fixtures/dumpdata <app or instance>
```
For example, running `saskatoon/fixtures/dumpdata member.city` will create a `member-city.json` file containing all instances from the `City` model (defined in `members.model.py`) currently stored in the database.
