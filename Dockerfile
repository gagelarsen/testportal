FROM tiangolo/uwsgi-nginx-flask:python3.8

ADD testportal /app/testportal
ADD testportal_api /app/testportal_api
ADD core /app/core
ADD static /app/static
ADD templates /app/templates

ADD manage.py   /app/manage.py
ADD uwsgi.ini  /app/

RUN python setup.py egg_info \
    && pip install $(grep -v '^\[' *.egg-info/requires.txt)
