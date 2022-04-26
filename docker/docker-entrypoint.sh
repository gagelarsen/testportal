#!/bin/bash

if [ -d /app/testportal ]; then
    echo "Update..."
    pushd /app/testportal
    git pull
    popd
else
    echo "Clone..."
    git clone -b master https://github.com/gagelarsen/testportal /app/testportal
fi

pushd /app/testportal
python -m pip install -r /tmp/requirements.txt
popd

echo "---"
cat /app/uwsgi.ini
echo "---"

/usr/local/bin/uwsgi --ini /app/uwsgi.ini