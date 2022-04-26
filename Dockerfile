FROM python:3

RUN apt-get update -qq \
    && apt-get -yqq install git tini   > /dev/null 

EXPOSE 8000

## Install Buildbot 
ADD requirements.txt /tmp/
RUN python -m pip install uwsgi
RUN pip install -r /tmp/requirements.txt

## Add other files
ADD docker/uwsgi.ini  /app/
ADD docker/docker-entrypoint.sh /

ADD core /app/testportal/core
ADD static /app/testportal/static
ADD templates /app/testportal/templates
ADD testportal /app/testportal/testportal
ADD testportal_api /app/testportal/testportal_api

ADD manage.py /app/testportal/manage.py

WORKDIR /app
ENTRYPOINT ["tini", "--"]
CMD ["/bin/bash", "/docker-entrypoint.sh"]
