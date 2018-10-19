=======
SERVEUR
=======


Prérequis
=========

* Ressources minimum serveur :

Un serveur disposant d'au moins de 1 Go RAM et de 10 Go d'espace disque.


* Disposer d'un utilisateur linux appartenant au groupe ``www-data``. Cette documentation présente la procédure à suivre pour un utlisateur nommé ``synthese``.



Installation et configuration du serveur
========================================

Installation pour Debian 7, 8, 9 et Ubuntu 14.04

:notes:

    Cette documentation concerne une installation sur Debian ou Ubuntu. Pour tout autre environemment les commandes sont à adapter.

:notes:

    Durant toute la procédure d'installation, travailler avec l'utilisateur ``synthese``. Ne changer d'utilisateur que lorsque la documentation le spécifie.

::

    su - 
    apt-get install apache2 libapache2-mod-proxy-html curl python-dev python-pip libpq-dev libgeos-dev supervisor
    pip install virtualenv
    adduser --home /home/synthese synthese
    usermod -g www-data synthese
    usermod -a -G root synthese
    adduser synthese sudo
    exit
 
    

:notes:
    
    Sur Debian 8, il est necessaire d'installer les paquets suivant pour faire fonctionner la librairie opencv
    
::

    sudo apt-get install -y libsm6 libxrender1 libfontconfig1 2>/var/log/geonature/install_log.log 
    sudo apt-get install -y python-qt4 2>/var/log/geonature/install_log.log



:notes:

    Sur Debian 9 libapache2-mod-proxy-html n'existe plus. L'application fonctionne sans ce paquet.

    
* Fermer la console et la réouvrir pour que les modifications soient prises en compte.

* Installer npm pour debian 7 et 8


  ::  
        
        su -
        sh -c 'echo "" >> /etc/apt/sources.list'
        sh -c 'echo "#Backports" >> /etc/apt/sources.list'
        sh -c 'echo "deb http://http.debian.net/debian wheezy-backports main" >> /etc/apt/sources.list'
        apt-get update
        aptitude -t wheezy-backports install nodejs
        update-alternatives --install /usr/bin/node nodejs /usr/bin/nodejs 100
        curl https://www.npmjs.com/install.sh | sh
        exit



* Installer npm pour debian 9


  ::  
        
        curl -sL https://deb.nodesource.com/setup_6.x | sudo bash -
        sudo apt install nodejs
        

* Activer le ``mod_rewrite`` et ``proxy_http`` et redémarrer Apache

  ::  
        
        sudo a2enmod rewrite
        sudo a2enmod proxy
        sudo a2enmod proxy_http
        sudo apache2ctl restart
     

Installation et configuration de PosgreSQL
==========================================

* Sur Debian 8, Postgres est livré en version 9.4 et postgis 2.1, vous pouvez sauter l'étape suivante. Sur Debian 7, il faut revoir la configuration des dépots pour avoir une version compatible de PostgreSQL (9.3) et PostGIS (2.1). Voir http://foretribe.blogspot.fr/2013/12/the-posgresql-and-postgis-install-on.html.

  ::  
        
        sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ wheezy-pgdg main" >> /etc/apt/sources.list'
        sudo wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
        sudo apt-get update
 
* Installation de PostreSQL/PostGIS pour Debian 8

  ::  
        
        sudo apt-get update
        sudo apt-get install postgresql postgresql-client
        sudo apt-get install postgresql-9.4-postgis-2.1
        sudo adduser postgres sudo
        
* Installation de PostreSQL/PostGIS pour Debian 7

  ::  
        
        sudo apt-get install postgresql-9.3 postgresql-client-9.3
        sudo apt-get install postgresql-9.3-postgis-2.1
        sudo adduser postgres sudo
        
* Configuration de PostgreSQL pour Debian 8 - permettre l'écoute de toutes les IP

  ::  
        
        sed -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" -i /etc/postgresql/9.4/main/postgresql.conf
        sudo sed -e "s/# IPv4 local connections:/# IPv4 local connections:\nhost\tall\tall\t0.0.0.0\/0\t md5/g" -i /etc/postgresql/9.4/main/pg_hba.conf
        /etc/init.d/postgresql restart
        
* Configuration de PostgreSQL pour Debian 7 - permettre l'écoute de toutes les IP

  ::  
        
        sed -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" -i /etc/postgresql/9.3/main/postgresql.conf
        sudo sed -e "s/# IPv4 local connections:/# IPv4 local connections:\nhost\tall\tall\t0.0.0.0\/0\t md5/g" -i /etc/postgresql/9.3/main/pg_hba.conf
        sudo /etc/init.d/postgresql restart

* Création de 2 utilisateurs PostgreSQL

  ::  
        
        sudo su postgres
        psql
        CREATE ROLE geonatuser WITH LOGIN PASSWORD 'monpassachanger';
        CREATE ROLE geonatadmin WITH SUPERUSER LOGIN PASSWORD 'monpassachanger';
        \q
        
L'utilisateur ``geonatuser`` sera le propriétaire de la base de données ``taxhubdb`` et sera utilisé par l'application pour se connecter à celle-ci.

L'utilisateur ``geonatadmin`` est super-utilisateur de PostgreSQL.

L'application fonctionne avec le mot de passe ``monpassachanger`` par defaut mais il est conseillé de le modifier !

Ce mot de passe, ainsi que les utilisateurs PostgreSQL créés ci-dessus (``geonatuser`` et ``geonatadmin``) sont des valeurs par défaut utilisées à plusieurs reprises dans l'application. Ils peuvent cependant être changés. S'ils doivent être changés, ils doivent l'être dans plusieurs fichiers de l'application ``settings.ini`` et ``config.py``.
