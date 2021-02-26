# shipanaro

## Requirements

You need native libraries for development dependencies of Python and Open LDAP because `python-ldap`
is a source distribution.

E.g. on Ubuntu:

    sudo apt install build-essential python3-dev libldap2-dev libsasl2-dev

For other platforms see [python-ldap docs](https://www.python-ldap.org/en/python-ldap-3.3.0/installing.html#build-prerequisites)

Alternatively, you may choose to use docker for development, in which case you don't need any other
dependencies than `docker` (including `docker-compose`) and `make`.

## The docker workflow (simplest, start here)

### Initial setup

> We assume you've cloned the repository and want to get things going for the first time.

First, get all systems up and running:

    make run

...this will build a docker image for the web app, and start all services (database,
LDAP, web).

Then you need to get the initial database set up (mostly apply migrations).

    make init-data

A couple of web apps you will be using:

- http://localhost:8000 - the shipanaro web application
- https://localhost:9876 - the PHP LDAP admin

### Set up an initial user

Make yourself a user in LDAP:

- Log in to LDAP using these credentials:
  - DN: cn=admin,dc=pirata,dc=cat
  - Password: admin
- On the sidebar menu, click on `dc=pirata,dc=cat (1)` and `Create new entry here`.
- Create a new `Generic Posix Group` named `militants`. Make sure you click `Create` and then
  `Commit`.
- Create a new `Generic User Account`. Make sure you chose the group `militants`, fill in all
  the data, click on `Create` and then `Commit`.

> To check the contents of LDAP, you can run `make ldap-list` at any time.

You can now log in to shipanaro with the user you just created in LDAP. After a successful login,
the user will be created in Django.

In order to get access to the Django admin site, you need to make this new user a superuser.
Open the django shell using:

    make shell

Within the shell:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
me = User.objects.get(username="txels")
me.is_staff = True
me.is_superuser = True
me.save()
```

You can now browse to `http://localhost:8000/__capitania__/` which is the URL of
the django admin.

### Running tests

    make test

## The "native" workflow - some tips if you're not fully using docker

### Set things up

```bash
apt install python3{,-pip}
pip3 install pipenv
cd $SHIPANARO_HOME
pipenv shell
pipenv install
```

...plus find a way to run postgres and LDAP. You can use docker for that ;)

### Run the app

Running things for the first time: since we include a custom user model in the `humans` app, running
migrations is a bit tricky - doing it in two steps solves the issue:
(Otherwise you may get an error `ValueError: Related model 'humans.user' cannot be resolved`)

> In order to run Django's `manage.py` you will have to set a bunch of environment variables.
> Check `docker-compose.yml` and the `web` service for reference.

```bash
pipenv shell
./manage.py migrate humans
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```

On subsequent updates, you will only need to optionally run migrations (if models have changed),
and run the server:

```
./manage.py migrate
./manage.py runserver
```

## Stuff you can do on the local site

Browse to the [admin page](http://localhost:8000/admin)
and log in with the superuser account you just created.

You can create a membership for your user account via the admin
and browse to the [profile page](http://localhost:8000/accounts/profile/)
to edit your membership (this is the end user-facing page).

## Front-end build

```bash
./manage.py collectstatic --no-input
yarn install
yarn build  # for development
yarn dist   # for production
```
