#!/bin/sh

# wait for PSQL server to start
sleep 10

# su -m anon_fl -c "psql -c \"CREATE USER anon_fl WITH PASSWORD 'anon_fl'; CREATE DATABASE anon_fl; ALTER USER anon_fl WITH ENCRYPTED PASSWORD 'anon_fl'\"; GRANT ALL PRIVELEGES ON DATABASE anon_fl TO anon_fl;"

su -m anon_fl -c "python manage.py makemigrations api"
su -m anon_fl -c "python manage.py migrate"

su -m anon_fl -c "gunicorn anon_fl.wsgi:application --bind :8000"
