#!/bin/sh

python manage.py loaddata user.json
python manage.py loaddata request_type.json
python manage.py loaddata request.json
