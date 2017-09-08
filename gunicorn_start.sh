#!/bin/bash

APP_NAME=taxhub
FLASKDIR=$(readlink -e "${0%/*}")
VENVDIR=venv
NUM_WORKERS=4
HOST=0.0.0.0
PORT=5000


echo "Starting $APP_NAME"
echo "$FLASKDIR"

# activate the virtualenv
cd $FLASKDIR/$VENVDIR
source bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH


# Start your unicorn
exec gunicorn  server:app --error-log /tmp/errors.log --pid="${APP_NAME}.pid" -w "${NUM_WORKERS}"  -b "${HOST}:${PORT}"  -n "${APP_NAME}"
