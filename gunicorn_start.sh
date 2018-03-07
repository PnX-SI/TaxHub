#!/bin/bash

FLASKDIR=$(readlink -e "${0%/*}")

echo "Starting $app_name"
echo "$FLASKDIR"

. "$FLASKDIR"/settings.ini

# activate the virtualenv
cd $FLASKDIR/$venv_dir
source bin/activate

export PYTHONPATH=$FLASKDIR:$PYTHONPATH


# Start your unicorn
if [ "$enable_https" = true ]
then
  exec gunicorn  server:app --certfile="${https_cert_path}" --keyfile="${https_key_path}" --access-logfile /var/log/taxhub/taxhub-access.log --error-log /var/log/taxhub/taxhub-errors.log --pid="${app_name}.pid" -w "${gun_num_workers}"  -b "${gun_host}:${gun_port}"  -n "${app_name}" --bind 0.0.0:443
else
  exec gunicorn  server:app --access-logfile /var/log/taxhub/taxhub-access.log
    --error-log /var/log/taxhub/taxhub-errors.log --pid="${app_name}.pid" -w "${gun_num_workers}"
    -b "${gun_host}:${gun_port}"  -n "${app_name}"
fi