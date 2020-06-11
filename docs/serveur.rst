=======
SERVEUR
=======


Prérequis
=========

* Ressources minimum serveur :

  Un serveur disposant d'au moins 1 Go de RAM et 10 Go d'espace disque.

* Disposer d'un utilisateur linux appartenant au groupe ``www-data``. Cette documentation présente la procédure à suivre pour un utlisateur nommé ``synthese``.

Installation et configuration du serveur
========================================

Installation pour Debian 9 et 10 et Ubuntu 18

:notes:

  Cette documentation concerne une installation sur Debian ou Ubuntu. Pour tout autre environemment, les commandes sont à adapter.

:notes:

  Durant toute la procédure d'installation, travaillez avec l'utilisateur courant (``synthese`` dans cette doc). Ne changez d'utilisateur que lorsque la documentation le spécifie.

* Se connecter au serveur, puis devenir administrateur (le mot de passe de l'utilisateur ``root`` vous sera demandé) :

  .. code-block:: bash

    su -

* Installez les paquets suivants :

  .. code-block:: bash

    apt-get install apache2 curl python-dev python-pip libpq-dev libgeos-dev supervisor sudo python3 python3-pip unzip git -y

* Tentez d'installer le paquet suivant:

  .. code-block:: bash

    apt-get install libapache2-mod-proxy-html -y

Ignorez toute erreur car sur certaines distributions, comme Debian 9, ``libapache2-mod-proxy-html`` n'existe plus. L'application fonctionne alors sans ce paquet.

* Créez un utilisateur dedié à TaxHub, ici appelé ``synthese`` :

  .. code-block:: bash

    adduser --gecos "" --home /home/synthese synthese

  La commande va vous demander de saisir un mot de passe. Durant la saisie du mot de passe, les lettres n'apparaissent pas quand vous les tapez. Ceci est normal.

  :notes:

    Notez ce mot de passe.

    Pour certaines commandes, des droits administrateurs sont nécessaires, et il faura les prefixer de ``sudo``. ``sudo`` peut vous demander un mot de passe, et c'est celui que nous venons juste de créer avec ``adduser`` qu'il faudra utiliser.

* Ajoutez l'utilisateur ``synthese`` aux groupes ``sudo``, ``root`` et ``www-data``:

  .. code-block:: bash

    adduser synthese sudo
    adduser synthese root
    adduser synthese www-data

:notes:
=======
* Connectez vous en tant qu'utilisateur ``synthese``. Le reste de l'installation se fera avec cet utilisateur dans son dossier personnel :

  .. code-block:: bash

    su synthese
    cd

* Installez l'outil python virtualenv :

  .. code-block:: bash

    python3 -m pip install virtualenv==20.0.1 --user

* Installez NVM (Node version manager) :

  .. code-block:: bash

    wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.6/install.sh | bash

    source ~/.bashrc

* Activez le ``mod_rewrite`` et ``proxy_http`` et redémarrez Apache :

  .. code-block:: bash

    sudo a2enmod rewrite proxy proxy_http

    sudo apache2ctl restart

Installation et configuration de PostgreSQL
===========================================

* Installation de PostreSQL/PostGIS pour **Debian 9** :

  On installe les paquets :

  .. code-block:: bash

    sudo apt-get install postgresql postgresql-client postgresql-9.6-postgis-2.3

    PG_VERSION="9.6"

* (OPTIONNEL) Autoriser des connections depuis l'extérieur

  Si votre base de données doit être accessible depuis un autre serveur, il faut changer sa configuration.

  **Ne le faites que si c'est absolument nécessaire.** Si tout ce que vous voulez faire, c'est installer TaxHub pour un autre service (GeoNature, GeoNature-citizen, etc) sur le même serveur, ce n'est PAS nécessaire.

  On édite le fichier de configuration :

  .. code-block:: bash

    sudo sed -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" -i /etc/postgresql/${PG_VERSION}/main/postgresql.conf

    sudo sed -e "s/# IPv4 local connections:/# IPv4 local connections:\nhost\tall\tall\t0.0.0.0\/0\t md5/g" -i /etc/postgresql/${PG_VERSION}/main/pg_hba.conf

    sudo /etc/init.d/postgresql restart

* Créez 2 utilisateurs PostgreSQL

  Think about a password for your database, then do :

  .. code-block:: bash

    sudo adduser postgres sudo

    sudo -u postgres -i createuser geonatuser --pwprompt

    sudo -u postgres -i createuser geonatadmin --pwprompt --superuser

  L'utilisateur ``geonatuser`` sera le propriétaire de la base de données ``taxhubdb`` et sera utilisé par l'application pour se connecter à celle-ci.

  L'utilisateur ``geonatadmin`` est super-utilisateur de PostgreSQL.

  Ce mot de passe, ainsi que les utilisateurs PostgreSQL créés ci-dessus (``geonatuser`` et ``geonatadmin``) sont des valeurs par défaut utilisées à plusieurs reprises dans l'application. Ils peuvent cependant être changés. S'ils doivent être changés, ils doivent l'être dans plusieurs fichiers de l'application ``settings.ini`` et ``config.py``.
