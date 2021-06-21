#!/bin/bash
. ../../../settings.ini

START_RED="\033[0;31m"
START_ORANGE="\033[0;33m"
START_GREEN="\033[0;32m"
NC="\033[0m"

mkdir -p /tmp/taxhub
sudo chown -R "$(id -u)" /tmp/taxhub


LOG_DIR="../../../var/log/updatetaxrefv13"

mkdir -p $LOG_DIR

# Test si aucune donnée de bib_noms n'a de cd_ref null
countemptycd_ref=`export PGPASSWORD=$user_pg_pass;psql -X -A -h $db_host -U $user_pg -d $db_name -t -c "SELECT count(*) FROM taxonomie.bib_noms WHERE cd_ref IS NULL;"`

if [ $countemptycd_ref -gt 0 ]
then
    echo "Il y a $countemptycd_ref donnée(s) n'ayant aucun cd_ref dans la table bib_noms"
    exit;
fi

echo "Import des données de taxref v13"

echo "Import des données de taxref v13" > $LOG_DIR/update_taxref_v13.log

array=( TAXREF_INPN_v13.zip)
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

sudo -n -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS intarray;' &>> $LOG_DIR/update_taxref_v13.log



echo "Import taxref v13"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.1.1_prepare_import_taxrefv13.sql   &>> $LOG_DIR/update_taxref_v13.log
sudo -u postgres -s psql -d $db_name  -f scripts/0.1.2_import_taxrefv13.sql   &>> $LOG_DIR/update_taxref_v13.log

echo "Export des cd_nom à modifier dans les données d'observations vers /tmp"
sudo -u postgres -s psql -d $db_name  -f scripts/0.1.3_cd_nom_disparu_synthese_export.sql &>> $LOG_DIR/update_taxref_v13.log

echo "Traitement bib_noms disparus"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/0.2.1_correction_cd_nom_disparus.sql &>> $LOG_DIR/update_taxref_v13.log
sudo -n -u postgres -s psql -d $db_name -f scripts/0.2.2_correction_cd_nom_disparus.sql &>> $LOG_DIR/update_taxref_v13.log


echo "Detection des changements"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.1_taxref_changes_detections.sql &>> $LOG_DIR/update_taxref_v13.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name  -f scripts/1.2_taxref_changes_detections_cas_actions.sql &>> $LOG_DIR/update_taxref_v13.log
sudo -n -u postgres -s psql -d $db_name  -f scripts/1.3_taxref_changes_detections_export.sql &>> $LOG_DIR/update_taxref_v13.log

echo "Export des bilans réalisés vers /tmp"
printf "${START_ORANGE}La clé primaire fk_bib_nom_taxref a été supprimée. Si vous abandonnez la migration en cours, par exemple après cette étape, vous pouvez la réactiver en exécutant le script sql suivant :${NC}\n"
printf "${START_GREEN}ALTER TABLE taxonomie.bib_noms ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom);${NC}\n"
echo ""
printf "${START_ORANGE}Visualisation des logs des opérations ci-dessus : ${NC}\n"
cat $LOG_DIR/update_taxref_v13.log