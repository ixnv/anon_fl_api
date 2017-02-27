#!/bin/sh

su -m anon_fl -c "psql -c \"CREATE USER anon_fl WITH PASSWORD 'anon_fl'; CREATE DATABASE anon_fl; ALTER USER anon_fl WITH ENCRYPTED PASSWORD 'anon_fl'\"; GRANT ALL PRIVELEGES ON DATABASE anon_fl TO anon_fl;"
