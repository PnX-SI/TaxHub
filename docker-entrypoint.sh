#!/bin/bash

set -euo pipefail

db_host=${POSTGRES_HOST:-db}
db_port=${POSTGRES_PORT:-5432}
db_user=${POSTGRES_USER:-geonatuser}
db_pass=${POSTGRES_PASSWORD:-monpassachanger}
db_name=${POSTGRES_DB:-geonature2db}

. create_sys_dir.sh

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    PGPASSWORD=$db_pass psql -h $db_host -p $db_port -U $db_user -tAl | grep -q "^$1|"
    return $?
}

function schema_exists () {
    q="SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = '$1');"
    r=`PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -X -A -t -c "$q"`
    if [ $r == 't' ]; then
      true
    else 
      false
    fi
}

function create_taxhub_db () {
    echo "Création de la base de données $db_name"
    PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -c "CREATE DATABASE $db_name;"
}

function create_taxhub_schema () {
	#Création des répertoires systèmes
    create_sys_dir

    echo "Ajout du language plpgsql et de l'extension pour les UUID..."
    PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -c "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog; COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';"
    PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
    # Mise en place de la structure de la base et des données permettant son fonctionnement avec l'application
    echo "Création de la structure de la base de données..."
    PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -f data/taxhub.sql 
    PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name -f data/generic_drop_and_restore_deps_views.sql 
    array=( TAXREF_INPN_v13.zip ESPECES_REGLEMENTEES_v11.zip LR_FRANCE_20160000.zip )
    for i in "${array[@]}"
    do
        if [ ! -f '/tmp/taxhub/'$i ]
        then
                wget http://geonature.fr/data/inpn/taxonomie/$i -P /tmp/taxhub
                unzip /tmp/taxhub/$i -d /tmp/taxhub
        else
            echo $i exists
        fi
    done
    echo "Insertion  des données taxonomiques de l'inpn... (cette opération peut être longue)"
    cd $DIR
    sudo -u postgres -s psql -d $db_name  -f data/inpn/data_inpn_taxhub.sql &>> $LOG_DIR/installdb/install_db.log

    echo "Création de la vue représentant la hierarchie taxonomique..."
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/materialized_views.sql  &>> $LOG_DIR/installdb/install_db.log

    echo "Insertion de données de base"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata.sql  &>> $LOG_DIR/installdb/install_db.log

    if $insert_geonatureatlas_data
    then
        echo "Insertion de données nécessaires à GeoNature-atlas"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_atlas.sql  &>> $LOG_DIR/installdb/install_db.log
    fi

	if $insert_attribut_example
    then
        echo "Insertion d'un exemple d'attribut"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_example.sql  &>> $LOG_DIR/installdb/install_db.log
    fi

	if $insert_taxons_example
    then
        echo "Insertion de 8 taxons exemple"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_taxons_example.sql  &>> $LOG_DIR/installdb/install_db.log
    fi

    if $insert_geonaturev1_data
    then
        echo "Insertion de données nécessaires à GeoNature V1"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_geonaturev1.sql  &>> $LOG_DIR/installdb/install_db.log
    fi

	if $insert_geonaturev1_data && $insert_taxons_example
    then
        echo "Insertion des 8 taxons exemple aux listes nécessaires à GeoNature V1"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_taxons_example_geonaturev1.sql  &>> $LOG_DIR/installdb/install_db.log
    fi

    if [ $users_schema = "local" ]
    then
        echo "Création du schéma Utilisateur..."
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub.sql -P /tmp
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-data.sql -P /tmp
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-dataset.sql -P /tmp
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub.sql &>> $LOG_DIR/installdb/install_db.log
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub-data.sql &>> $LOG_DIR/installdb/install_db.log
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/usershub-dataset.sql &>> $LOG_DIR/installdb/install_db.log
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/adds_for_usershub.sql &>> $LOG_DIR/installdb/install_db.log
	    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/adds_for_usershub_views.sql &>> $LOG_DIR/installdb/install_db.log
    else
        echo "Connexion à la base Utilisateur..."
        cp data/create_fdw_utilisateurs.sql /tmp/taxhub/create_fdw_utilisateurs.sql
        cp data/grant.sql /tmp/taxhub/grant.sql
        sed -i "s#\$user_pg#$user_pg#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_host#$usershub_host#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_db#$usershub_db#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_port#$usershub_port#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_user#$usershub_user#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_pass#$usershub_pass#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_user#$usershub_user#g" /tmp/taxhub/grant.sql
        sudo -u postgres -s psql -d $db_name -f /tmp/taxhub/create_fdw_utilisateurs.sql  &>> $LOG_DIR/installdb/install_db.log
        sudo -u postgres -s psql -d $db_name -f /tmp/taxhub/grant.sql
    fi
}

until pg_isready -h $db_host -p $db_port
do
  echo "Awaiting Database container"
  sleep 1
done
sleep 2


if database_exists $db_name; then
    if ${DROP_APPS_DB:-false}
        then
        echo "Suppression de la base..."
        PGPASSWORD=$db_pass psql -h $db_host -U $db_user -p $db_port -d $db_name "DROP DATABASE IF EXISTS $db_name";
	create_taxhub_db
	create_taxhub_schema
    else
        if ! schema_exists taxonomie; then
            echo "Le schéma utilisateur existe déjà, aucune action ne sera effectuée"
	    create_taxhub_schema
	else
            echo "La base de données et le schéma utilisateurs existe déjà, aucune modification ne sera effectuée"
        fi
    fi
fi

if ! database_exists $db_name; then
	create__db
	create_taxhub_schema
fi

if [ ! -f ./config/config.py ]; then
    echo "generate config file"
    echo "# Config generated by docker-entrypoint.sh" >> ./config/config.py
    echo "SQLALCHEMY_DATABASE_URI = \"postgresql://$db_user:$db_pass@$db_host:$db_port/$db_name\"" >> ./config/config.py
    echo "SQLALCHEMY_TRACK_MODIFICATIONS = False" >> ./config/config.py
    echo "" >> ./config/config.py
    echo "# ID of TaxHub application" >> ./config/config.py
    echo "ID_APP = ${ID_APP:-2}" >> ./config/config.py
    echo "" >> ./config/config.py
    echo "# Authentification crypting method (hash or md5)" >> ./config/config.py
    echo "" >> ./config/config.py
    echo "COOKIE_EXPIRATION = ${COOKIE_EXPIRATION:-3600}" >> ./config/config.py
    echo "DEBUG=True" >> ./config.py
    echo "SESSION_TYPE = 'filesystem'" >> ./config.py
    echo "SECRET_KEY = '${SECRETKEY:-$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c50)}'" >> ./config/config.py
    echo "COOKIE_EXPIRATION = 3600" >> ./config.py
    echo "" >> ./config.py
    echo "# File" >> ./config.py
    echo "import os" >> ./config.py
    echo "BASE_DIR = os.path.abspath(os.path.dirname(__file__))" >> ./config.py
    echo "PLOAD_FOLDER = 'static/medias'" >> ./config.py
    echo "# Authentification crypting method (hash or md5)" >> ./config.py
    echo "PASS_METHOD='hash'" >> ./config.py
    echo "" >> ./config/config.py
    echo "PORT = ${PORT:-5001}" >> ./config/config.py
    echo "DEBUG = ${DEBUG:-False}" >> ./config/config.py
    echo "" >> ./config/config.py
    echo "ACTIVATE_API = ${ACTIVATE_API:-True}" >> ./config/config.py
    echo "ACTIVATE_APP = ${ACTIVATE_APP:-True}" >> ./config/config.py
else
    echo "config file already exists"
fi

# Start App
echo ""
echo "READY TO START USERSHUB APPLICATION ON PORT ${PORT:-5001}"
echo ""
gunicorn -w ${WORKERS:-1} --access-logfile - -b 0.0.0.0:${PORT:-5001} server:app
