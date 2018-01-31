#!/bin/bash

. ../../../settings.ini

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f 5_clean_db &>> ../../../logs/update_taxref_v11.log
