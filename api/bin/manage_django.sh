#!/bin/bash
SRC=$(cd $(dirname "$0")/../src; pwd)
cd $SRC
python manage.py "$@"
