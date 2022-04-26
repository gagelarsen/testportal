FROM python:3

RUN apt-get update -qq \
    && apt-get -yqq install git tini   > /dev/null 

## Install Buildbot 
ADD requirements.txt /tmp/
RUN python -m pip install uwsgi
RUN pip install -r /tmp/requirements.txt

## Add other files
ADD docker/uwsgi.ini  /app/
ADD docker/docker-entrypoint.sh /

WORKDIR /app
ENTRYPOINT ["tini", "--"]
CMD ["/bin/bash", "/docker-entrypoint.sh"]
