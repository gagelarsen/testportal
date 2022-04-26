#!/bin/bash
pushd /app/testportal
python -m pip install -r /tmp/requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
popd

/usr/local/bin/uwsgi --ini /app/uwsgi.ini