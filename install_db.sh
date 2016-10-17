#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

#include user config = settings.ini
. settings.ini

#get app path
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
        then
        # Argument is null
        return 0
    else
        # Grep db name in the list of database
        sudo -n -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}


if database_exists $db_name
then
        if $drop_apps_db
            then
            echo "Suppression de la base..."
            sudo -n -u postgres -s dropdb $db_name
        else
            echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
        fi
fi
if ! database_exists $db_name
then
    echo "Création de la base..."
    sudo -n -u postgres -s createdb -O $user_pg $db_name

    # Mise en place de la structure de la base et des données permettant son fonctionnement avec l'application

    echo "Création de la structure de la base..."
    rm logs/install_db.log
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdb.sql  &>> logs/install_db.log

    echo "Décompression des fichiers du taxref..."
    cd data/inpn
    unzip TAXREF_INPN_v9.0.zip -d /tmp
  	unzip ESPECES_REGLEMENTEES.zip -d /tmp

    echo "Insertion  des données taxonomiques de l'inpn... (cette opération peut être longue)"
    cd $DIR
    export PGPASSWORD=$admin_pg_pass;psql -h $db_host -U $admin_pg -d $db_name  -f data/inpn/data_inpn_v9_taxhub.sql &>> logs/install_db.log

    echo "Création de la vue représentant la hierarchie taxonomique..."
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/vm_hierarchie_taxo.sql  &>> logs/install_db.log

    echo "Insertion de données exemples..."
    export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/taxhubdata.sql  &>> logs/install_db.log

    if [ $users_schema = "local" ]
        then
        echo "Création du schéma Utilisateur..."
        export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/create_utilisateurs.sql  &>> logs/install_db.log
    else
        echo "Connexion à la base Utilisateur..."
        cp data/create_fdw_utilisateurs.sql /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$user_pg#$user_pg#g" /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_host#$usershub_host#g" /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_db#$usershub_db#g" /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_port#$usershub_port#g" /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_user#$usershub_user#g" /tmp/create_fdw_utilisateurs.sql
        sed -i "s#\$usershub_pass#$usershub_pass#g" /tmp/create_fdw_utilisateurs.sql
        export PGPASSWORD=$admin_pg_pass;psql -h $db_host -U $admin_pg -d $db_name -f /tmp/create_fdw_utilisateurs.sql  &>> logs/install_db.log
    fi
    
    # suppression des fichiers : on ne conserve que les fichiers compressés
    echo "nettoyage..."
    rm /tmp/*.txt
    rm /tmp/*.csv
fi
