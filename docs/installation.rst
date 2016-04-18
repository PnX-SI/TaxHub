===========
APPLICATION
===========

Configuration de la base de données PostgreSQL
==============================================

* mettre à jour le fichier ``config/settings.ini``

    :: nano config/settings.ini

Renseigner le nom de la base de données, les utilisateurs PostgreSQL et les mots de passe. Il est possible mais non conseillé de laisser les valeurs proposées par défaut. 

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh``. Les utilisateurs PostgreSQL doivent être en concordance avec ceux créés lors de la dernière étape de l'installation serveur ``Création de 2 utilisateurs PostgreSQL``. 


Création de la base de données
==============================

* Création de la base de données et chargement des données initiales

    ::
    
        cd /home/synthese/geonature
        sudo ./install_db.sh

* Si besoin, l'exemple des données SIG du Parc national des Ecrins pour les tables du schéma ``layers``
  
  ::

    export PGPASSWORD=monpassachanger;psql -h databases -U geonatuser -d geonaturedb -f pne/data_sig_pne_2154.sql 
    
Installation de l'application
=============================

* Installation des dépendances avec composer

    ::
    
        echo "run composer install"
        composer install

* Configuration des droits des répertoires de l'application...

    ::
    
        chmod -R 777 app/logs app/cache
        php app/console cache:clear --env=prod
        chmod -R 777 app/logs app/cache
