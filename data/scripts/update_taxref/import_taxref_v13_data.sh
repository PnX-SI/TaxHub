#!/bin/bash
. ../../../settings.ini

mkdir -p /tmp/taxhub
sudo chown -R "$(id -u)" /tmp/taxhub


LOG_DIR="../../../var/log/updatetaxrefv13"

mkdir -p $LOG_DIR

echo "Import des données de taxref v13"

echo "Import des données de taxref v13" > $LOG_DIR/update_taxref_v13.log

array=( TAXREF_INPN_v13.zip BDC_STATUTS_13.zip)
for i in "${array[@]}"
do
    if [ ! -f '/tmp/taxhub/'$i ]
    then
        wget http://geonature.fr/data/inpn/taxonomie/$i -P /tmp/taxhub
    else
        echo $i exists
    fi
    unzip -o /tmp/taxhub/$i -d /tmp/taxhub &>> $LOG_DIR/update_taxref_v13.log
done


echo "Import taxref v13"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.1.1_prepare_import_taxrefv13.sql   &>> $LOG_DIR/update_taxref_v13.log
sudo -u postgres -s psql -d $db_name  -f scripts/0.1.2_import_taxrefv13.sql   &>> $LOG_DIR/update_taxref_v13.log

echo "Export des cd_nom à modifier dans les données d'observations"
sudo -u postgres -s psql -d $db_name  -f scripts/0.1.3_cd_nom_disparu_synthese_export.sql &>> $LOG_DIR/update_taxref_v13.log

echo "Traitement bib_noms disparus"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.2_correction_cd_nom_disparus.sql &>> $LOG_DIR/update_taxref_v13.log


echo "Detection des changements"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.1_taxref_changes_detections.sql &>> $LOG_DIR/update_taxref_v13.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.2_taxref_changes_detections_cas_actions.sql &>> $LOG_DIR/update_taxref_v13.log
sudo -n -u postgres -s psql -d $db_name  -f scripts/1.3_taxref_changes_detections_export.sql &>> $LOG_DIR/update_taxref_v13.log

echo "Export des bilans réalisés dans tmp"
