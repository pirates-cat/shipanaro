# shipanaro

## Quick install

```bash
apt-get install python3{,-pip}
pip3 install pipenv
cd $SHIPANARO_HOME
pipenv shell
pipenv install
```


## Run locally

```bash
pipenv shell
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```

### Stuff you can do on the local site

Browse to the [admin page](http://localhost:8000/admin)
and log in with the superuser account you just created.

You can create a membership for your user account via the admin
and browse to the [profile page](http://localhost:8000/accounts/profile/)
to edit your membership (this is the end user-facing page).
