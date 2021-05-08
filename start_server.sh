#!/bin/sh

gunicorn index:server -b :8081 -t 900 \
--workers 3 --error-logfile output.log \
--access-logfile access.log --capture-output --log-level debug
