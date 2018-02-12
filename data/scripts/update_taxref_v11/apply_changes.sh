#!/bin/bash

. ../../../settings.ini


echo "Detection des changements"

file_name="scripts/2.1_taxref_changes_corrections_pre_detections.sql"
if test -e "$file_name";then
    echo "  Corrections prédétection"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f $file_name &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
fi
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.2_taxref_changes_detections_cas_actions.sql &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log

countconflicts=`export PGPASSWORD=$user_pg_pass;psql -X -A -h $db_host -U $user_pg -d $db_name -t -c "SELECT count(*) FROM tmp_taxref_changes.comp_grap WHERE action ilike '%Conflict%';"`

if [ $countconflicts -gt 0 ]
then 
    echo "Il y a $countconflicts conflits non résolus qui empechent la mise à jour de taxref"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.3_taxref_changes_detections_export.sql &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
    exit;
fi

file_name="scripts/2.2_taxref_changes_corrections_post_detections.sql"
if test -e "$file_name";then
    echo "  Corrections postdétection"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f $file_name &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
fi

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.3_taxref_changes_detections_export.sql &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
echo "Export des bilans réalisés dans tmp"


echo "Mise à jour des statuts de protections"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/4.1_stpr_import_data.sql &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log

file_name="scripts/4.2_stpr_update_concerne_mon_territoire.sql"
if test -e "$file_name";then
    echo "  MAJ données concerne mon territoire"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f $file_name &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
fi

echo "Mise à jour des statuts de protections réalisés"


echo "Mise à jour des vues matérialisées"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f ../../refresh_materialized_view.sql &>> /var/log/taxhub/updatetaxrefv11/apply_changes.log
