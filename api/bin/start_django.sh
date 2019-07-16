#!/bin/bash
SRC=$(cd $(dirname "$0")/../src; pwd)
cd $SRC
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 --insecure
