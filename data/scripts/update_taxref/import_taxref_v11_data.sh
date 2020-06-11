#!/bin/bash
. ../../../settings.ini

mkdir -p /tmp/taxhub
sudo chown -R "$(id -u)" /tmp/taxhub


LOG_DIR="../../../var/log/updatetaxrefv11"

mkdir -p $LOG_DIR

echo "Import des données de taxref v11"

echo "Import des données de taxref v11" > $LOG_DIR/update_taxref_v11.log
array=( TAXREF_INPN_v11.zip ESPECES_REGLEMENTEES_v11.zip )
for i in "${array[@]}"
do
    if [ ! -f '/tmp/taxhub/'$i ]
    then
        wget http://geonature.fr/data/inpn/taxonomie/$i -P /tmp/taxhub
    else
        echo $i exists
    fi
    unzip -o /tmp/taxhub/$i -d /tmp/taxhub &>> $LOG_DIR/update_taxref_v11.log
done


echo "Import taxref v11"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.1_import_taxrefv11.sql   &>> $LOG_DIR/update_taxref_v11.log

echo "Traitement bib nom disparus"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.2_correction_cd_nom_disparus.sql &>> $LOG_DIR/update_taxref_v11.log


echo "Detection des changements"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.1_taxref_changes_detections.sql &>> $LOG_DIR/update_taxref_v11.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.2_taxref_changes_detections_cas_actions.sql &>> $LOG_DIR/update_taxref_v11.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.3_taxref_changes_detections_export.sql &>> $LOG_DIR/update_taxref_v11.log

echo "Export des bilans réalisés dans tmp"