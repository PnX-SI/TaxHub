#!/usr/bin/env bash

set -o pipefail

# Make sure only root can run our script
if [ "$(id -u)" == 0 ]; then
   echo "This script must not be run as root" 1>&2
   exit 1
fi


if [ ! -f settings.ini ]; then
  cp settings.ini.sample settings.ini
fi

nano settings.ini

#include user config = settings.ini
. settings.ini
 
#get app path
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
LOG_FILE=$DIR/install_db.log


function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
        then
        # Argument is null
        return 0
    else
        # Grep db name in the list of database
        sudo -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}


if database_exists $db_name
then
    if $drop_apps_db
        then
        echo "Suppression de la base..."
        sudo -u postgres -s dropdb $db_name
    else
        echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
    fi
fi

if ! database_exists $db_name
then
    echo "Création de la base..."
    sudo -u postgres -s createdb -O $user_pg $db_name

    sudo -n -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" &> $LOG_FILE

    sudo -n -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";' &>> $LOG_FILE

    sudo -n -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "postgis";' &>> $LOG_FILE

    echo "Extracting PostGIS version..."
    postgis_full_version=$(sudo -u postgres -s psql -d "${db_name}" -c "SELECT PostGIS_Version();")
    postgis_short_version=$(echo "${postgis_full_version}" | sed -n 's/^\s*\([0-9]*\.[0-9]*\)\s.*/\1/p')
    echo "PostGIS full version: ${postgis_full_version}"
    echo "PostGIS short version extract: '${postgis_short_version}'"

    echo "Adding Raster PostGIS extension if necessary..."
    postgis_required_version="3.0"
    if [[ "$(printf '%s\n' "${postgis_required_version}" "${postgis_short_version}" | sort -V | head -n1)" = "${postgis_required_version}" ]]; then
        echo "PostGIS version greater than or equal to ${postgis_required_version} --> adding Raster extension"
        sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgis_raster;" &>> $LOG_FILE
    else
        echo "PostGIS version lower than ${postgis_required_version} --> do nothing"
    fi

    sudo -n -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "unaccent";' &>> $LOG_FILE

    # Mise en place de la structure de la base et des données permettant son fonctionnement avec l'application

    source venv/bin/activate

    if [ $users_schema != "local" ]; then
        echo "Connexion à la base Utilisateur..."
        mkdir -p /tmp/taxhub/
        cp data/create_fdw_utilisateurs.sql /tmp/taxhub/create_fdw_utilisateurs.sql
        cp data/grant.sql /tmp/taxhub/grant.sql
        sed -i "s#\$user_pg#$user_pg#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_host#$usershub_host#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_db#$usershub_db#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_port#$usershub_port#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_user#$usershub_user#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_pass#$usershub_pass#g" /tmp/taxhub/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_user#$usershub_user#g" /tmp/taxhub/grant.sql
        sudo -u postgres -s psql -d $db_name -f /tmp/taxhub/create_fdw_utilisateurs.sql  &>> $LOG_FILE
        sudo -u postgres -s psql -d $db_name -f /tmp/taxhub/grant.sql  &>> $LOG_FILE
        flask db stamp 72f227e37bdf  # utilisateurs-samples
    fi

    flask db upgrade taxhub-standalone@head -x local-srid=2154
    flask db upgrade taxhub-standalone-sample@head
    flask db upgrade ref_geo_fr_departments@head
    flask db autoupgrade

    flask taxref import-v17 --taxref-region=${taxref_region:-fr}

    if $insert_geonatureatlas_data
    then
        echo "Insertion de données nécessaires à GeoNature-atlas"
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata_atlas.sql  &>> $LOG_FILE
    fi

    # Vaccum database
    echo "Vaccum database ... (cette opération peut être longue)"
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -c "VACUUM FULL VERBOSE;"  &>> $LOG_FILE

fi
