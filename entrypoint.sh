#!/bin/bash
# Entrypoint for docker image

python manage.py migrate humans
python manage.py migrate
gunicorn -b0.0.0.0 shipanaro.wsgi
