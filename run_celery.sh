#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

su -m anon_fl -c "celery worker -A api.celeryconf"
