#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" == 0 ]; then
   echo "This script must not be run as root" 1>&2
   exit 1
fi

# Create a specific variable to detect docker environment
DOCKERENV=${DOCKERENV:-false}

#Création des répertoires systèmes
. create_sys_dir.sh
create_sys_dir

function schema_exists () {
    q="SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = '$1');"
    r=`$psql_command -XAtc "$q"`
    echo "$q: $r"
    if [ $r='t' ]; then
      true
    else 
      false
    fi
}


if ! $DOCKERENV ; then
  if [ ! -f settings.ini ]; then
    cp settings.ini.sample settings.ini
  fi

  nano settings.ini

  #include user config = settings.ini
  . settings.ini

  #get app path

  psql_su_command="sudo -n -u postgres -s psql -d $db_name"
else 
  psql_su_command="psql -h ${db_host:-db} -p ${db_port:-5432} -U ${user_pg} -d ${db_name}"
fi  
psql_command="psql -h ${db_host:-db} -p ${db_port:-5432} -U ${user_pg} -d ${db_name}"

export PGPASSWORD=$user_pg_pass

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
LOG_DIR=$DIR/var/log

function database_exists () {
  # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
  # as appropriate.
  if [ -z $1 ]
      then
      # Argument is null
      return 0
  else
    # Grep db name in the list of database
    if ! $DOCKERENV ; then
      sudo -u postgres -s -- psql -tAl | grep -q "^$1|"	
    else   
      PGPASSWORD=$user_pg_pass psql -h $db_host -p $db_port -U $user_pg -tAl | grep -q "^$1|"
    fi
  fi
  return $?
}

if ! $DOCKERENV; then
  function create_db () {
    echo "Création de la base de données $db_name"
    sudo -u postgres -s createdb -O $user_pg $db_name
  }
else 
	# Pas de fonction create_db si on est en environnement docker, géré dans un autre conteneur, généralement géré dans le conteneur de base de données
  function create_db () {
    echo "Création de base de données non implantée en environnement Docker"
  }
fi

function init_db () {
  echo $PGPASSWORD
  $psql_su_command -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
  $psql_su_command -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";' 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
  $psql_su_command -c 'CREATE EXTENSION IF NOT EXISTS "pg_trgm";' 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
}

function create_taxonomie_schema () {

    # Mise en place de la structure de la base et des données permettant son fonctionnement avec l'application

    echo "Création de la structure de la base..."
    $psql_command -f data/taxhubdb.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
    $psql_command -f data/generic_drop_and_restore_deps_views.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log

    echo "Décompression des fichiers du taxref..."

    array=( TAXREF_INPN_v13.zip ESPECES_REGLEMENTEES_v11.zip LR_FRANCE_20160000.zip BDC_STATUTS_13.zip)
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
    $psql_su_command  -f data/inpn/data_inpn_taxhub.sql 2>&1 | tee -a $LOG_DIR/installdb/install_db.log

    echo "Création de la vue représentant la hierarchie taxonomique..."
    $psql_command -f data/materialized_views.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log

    echo "Insertion de données de base"
    $psql_command -f data/taxhubdata.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log

    echo "Insertion de fonctions génériques de détection de vues dépendantes"
    $psql_command -f data/generic_drop_and_restore_deps_views.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log

    if $insert_geonatureatlas_data
    then
        echo "Insertion de données nécessaires à GeoNature-atlas"
        $psql_command -f data/taxhubdata_atlas.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
    fi

	if $insert_attribut_example
    then
        echo "Insertion d'un exemple d'attribut"
        $psql_command -f data/taxhubdata_example.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
    fi

	if $insert_taxons_example
    then
        echo "Insertion de 8 taxons exemple"
        $psql_command -f data/taxhubdata_taxons_example.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
    fi

    if [ $users_schema = "local" ]
    then
        echo "Création du schéma Utilisateur..."
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub.sql -P /tmp
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-data.sql -P /tmp
        wget https://raw.githubusercontent.com/PnX-SI/UsersHub/$usershub_release/data/usershub-dataset.sql -P /tmp
        $psql_command -f /tmp/usershub.sql 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
        $psql_command -f /tmp/usershub-data.sql 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
        $psql_command -f /tmp/usershub-dataset.sql 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
        $psql_command -f data/adds_for_usershub.sql 2>&1 | tee -a $LOG_DIR/installdb/install_db.log
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
        $psql_su_command -f /tmp/taxhub/create_fdw_utilisateurs.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
        $psql_su_command -s psql -d $db_name -f /tmp/taxhub/grant.sql  2>&1 | tee -a $LOG_DIR/installdb/install_db.log
    fi

    # Vaccum database
    echo "Vaccum database ... (cette opération peut être longue)"
    $psql_command -c "VACUUM FULL VERBOSE;"  2>&1 | tee -a $LOG_DIR/installdb/install_db.log

}

if database_exists $db_name
then
  echo "La base de données $db_name existe déjà"
  if $drop_apps_db
  then
    echo "Suppression de la base..."
    sudo -u postgres -s dropdb $db_name
    create_db $db_name
    init_db
    create_taxonomie_schema
  else
    if ! schema_exists taxonomie; then
		  echo "Le schéma n'existe pas, il va être installé"

      init_db
      create_taxonomie_schema
    else
 	  if schema_exists taxonomie; then
	      	  echo "La base de données existe et le fichier de settings indique de ne pas la supprimer."
		  init_db
		  create_taxonomie_schema
	  else
		  echo "Init DB"
		  init_db
		  create_taxonomie_schema
	  fi
    fi
  fi
fi


if ! database_exists $db_name
then
  create_db $db_name
  init_db
  create_taxonomie_schema
fi
