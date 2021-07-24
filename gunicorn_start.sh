#!/bin/bash

FLASKDIR=$(readlink -e "${0%/*}")

echo "Starting $app_name"
echo "$FLASKDIR"

. "$FLASKDIR"/settings.ini

if [ ! -z "$proxy_http" ] || [ ! -z "$proxy_https" ]
then
    echo "\$proxy_http is NOT empty"
    export HTTP_PROXY="'$proxy_http'"
    export HTTPS_PROXY="'$proxy_https'"
fi

# activate the virtualenv
cd $FLASKDIR/$venv_dir
source bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH


# Start your unicorn
exec gunicorn  server:app --access-logfile $FLASKDIR/var/log/taxhub-access.log --pid="${app_name}.pid" --error-log $FLASKDIR/var/log/taxhub-errors.log -w "${gun_num_workers}" -b "${gun_host}:${gun_port}"  -n "${app_name}"
