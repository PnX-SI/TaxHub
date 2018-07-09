#!/bin/bash

. ../../../settings.ini


LOG_DIR="../../../var/log/updatetaxrefv11"

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/5_clean_db.sql &>> $LOG_DIR/clean_db.log
