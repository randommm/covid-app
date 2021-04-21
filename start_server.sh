#!/bin/sh

gunicorn dash_server:server -b :8001 -t 900 \
--workers 3 --error-logfile output.log \
--access-logfile access.log --capture-output --log-level debug \
--certfile /home/marco/.config/certbot/conf/live/server.marcoinacio.com/fullchain.pem  --keyfile /home/marco/.config/certbot/conf/live/server.marcoinacio.com/privkey.pem --do-handshake-on-connect
