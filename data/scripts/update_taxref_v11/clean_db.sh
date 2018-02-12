#!/bin/bash

. ../../../settings.ini

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f 5_clean_db &>> /var/log/taxhub/updatetaxrefv11/clean_db.log
