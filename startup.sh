#!/bin/bash

cd /var/app || exit

uwsgi --ini uwsgi/uwsgi.ini &

nginx -g "daemon off;"
