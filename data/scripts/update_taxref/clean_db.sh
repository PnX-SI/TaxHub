#!/bin/bash

. ../../../settings.ini

taxref_version="${1:-14}"

LOG_DIR="../../../var/log/updatetaxrefv${taxref_version}"
mkdir -p $LOG_DIR

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/5_clean_db.sql &>> $LOG_DIR/clean_db.log
