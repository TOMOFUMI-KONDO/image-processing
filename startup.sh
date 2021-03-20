#!/bin/bash

cd /var/app || exit

sleep 3

uwsgi --ini uwsgi/uwsgi.ini &

nginx -g "daemon off;"
