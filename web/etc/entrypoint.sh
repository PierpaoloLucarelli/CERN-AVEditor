#!/bin/bash

echo 'Starting app...'
cp -rf /opt/app-root/app-temp/* /opt/app-root/app
# We run the application using uwsgi
uwsgi --ini /opt/app-root/etc/uwsgi.ini