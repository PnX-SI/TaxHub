============
INSTALLATION
============

Cette documentation décrit l'installation indépendante de TaxHub. Il est aussi possible de réaliser l'installation avec le script automatisé d'installation globale de GeoNature (http://docs.geonature.fr/installation.html#installation-globale).

Prérequis
=========

Pour installer TaxHub, il vous faut un serveur avec Debian 10 ou 11.
L’utilisation de TaxHub avec une autre distribution est théoriquement possible, mais n’est pas officiellement supporté.

Vous devez avoir utiliser un éditeur de texte en console tel que ``nano``. Si vous ne savez pas comment faire, suivez ce tutoriel: https://openclassrooms.com/fr/courses/43538-reprenez-le-controle-a-laide-de-linux/39267-nano-lediteur-de-texte-du-debutant

Création d’un utilisateur
=========================

Vous devez disposer d'un utilisateur Linux pour faire tourner TaxHub (nommé ``synthese`` dans notre exemple). L’utilisateur doit appartenir aux groupes ``sudo`` et ``www-data``. Le répertoire de cet utilisateur ``synthese`` doit être dans ``/home/synthese``. Si vous souhaitez utiliser un autre utilisateur Linux, vous devrez adapter les lignes de commande proposées dans cette documentation.

::

    $ adduser --home /home/synthese synthese
    $ adduser synthese sudo
    $ adduser synthese www-data

:Note:

    Pour la suite de l'installation, veuillez utiliser l'utilisateur Linux créé précedemment (``synthese`` dans l'exemple), et non l'utilisateur ``root``.

Installation des dépendances requises
=====================================

Installez les dépendances suivantes :

::

    $ sudo apt install -y apache2 python3-pip python3-venv libpq-dev libgdal-dev sudo unzip
    $ sudo apt install -y postgresql postgresql-postgis

Installer NVM (Node version manager), node et npm :

::

    $ wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash


Fermer la console et la réouvrir pour que l’environnement npm soit pris en compte.

Configuration de PostgresQL
===========================

Créer un utilisateur PostgreSQL :

::

    $ sudo -u postgres createuser geonatadmin --pwpromt

Récupération du code source de TaxHub
=====================================

Récupérer le zip de l’application sur le Github du projet (`X.Y.Z à remplacer par le numéro de version souhaité <https://github.com/PnX-SI/TaxHub/releases>`_), dézippez le dans le répertoire ``/home/synthese`` :

.. code-block:: bash

    $ cd /home/synthese
    $ wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
    $ unzip X.Y.Z.zip
    $ mv TaxHub-X.Y.Z taxhub
    $ rm X.Y.Z.zip
    $ cd taxhub

Configuration de TaxHub
=======================

* Créer et mettre à jour le fichier ``settings.ini`` :

.. code-block:: bash

    $ cp settings.ini.sample settings.ini
    $ nano settings.ini

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh`` et par le script ``install_app.sh``.

Renseignez les informations nécessaires à la connexion à la base de données PostgreSQL. Il est possible de laisser la plupart des valeurs proposées par défaut, mais lisez au moins le fichier de bout en bout pour savoir ce qu'il est possible de changer.

La valeur la plus importante à mettre à jour est:

::

  user_pg_pass=monpassachanger

``monpassachanger`` doit être remplacé par la celui choisi lors de l’étape de configuration de PostgreSQL.


Stockage des media
------------------

Les media associés aux taxons peuvent être stockés sur le serveur (paramètre ``MEDIA_FOLDER``).

Il est possible d'utiliser le service de stockage S3 AWS en le "montant"
dans le système de fichier en utilisant notamment le paquet `s3fs` <https://manpages.debian.org/stretch/s3fs/s3fs.1>



Installation de l'application
=============================

Lancez le fichier d'installation et de configuration de l'application

.. code-block:: bash

  ./install_app.sh


Remplissage de la base de données
=================================

Lanceé le fichier d'installation et de préparation de la base de données :

.. code-block:: bash

  $ cd ~/taxhub
  $ ./install_db.sh

Le script va ouvrir une nouvelle fois le fichier de configuration settings.ini avec nano, pour vous donner une opportunité de revoir une dernière fois ces paramètres. Vous pouvez sauvegarder le fichier tel quel pour continuer (ctrl + x).


Arrêter/Lancer l'application
============================

* Pour arrêter TaxHub

::

    $ sudo systemctl stop taxhub

* Pour démarrer TaxHub

::

    $ sudo supervisorctl start taxhub


Configuration Apache
====================

Voici une des manières de configurer Apache. Elle se base sur le fait que la configuration ``/etc/apache2/sites-available/000-default.conf`` existe par défaut et va automatiquement charger notre nouvelle entrée.

Le script d’installation crée le ficher ``/etc/apache2/conf-available/taxhub.conf`` et l’active (``a2enconf taxhub``).
Ce fichier vous permet d’accéder à TaxHub via l’URL http://ADRESSE_DU_SERVEUR/taxhub/. Pour trouver l'adresse du serveur, faite:

.. code-block:: bash

  $ curl https://ipinfo.io/ip


Mise à jour de l'application
=============================

Les différentes versions de TaxHub sont disponibles sur le Github du projet (https://github.com/PnX-SI/TaxHub/releases)

* Lire attentivement les notes de chaque version si il y a des spécificités (https://github.com/PnX-SI/TaxHub/releases). Suivre ces instructions avant de continuer la mise à jour.

* Télécharger et extraire la version souhaitée dans un répertoire séparé (où ``X.Y.Z`` est à remplacer par le numéro de la version que vous installez) :

  ::

        cd
        wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
        unzip X.Y.Z.zip
        mv taxhub taxhub_old
        mv TaxHub-X.Y.Z/ taxhub
        rm X.Y.Z.zip

* Récupérer les anciens fichiers de configuration :

  ::

        cp taxhub_old/settings.ini taxhub/settings.ini
        cp taxhub_old/apptax/config.py taxhub/apptax/config.py
        cp taxhub_old/static/app/constants.js taxhub/static/app/constants.js

* Récupérer les médias uploadés dans la précédente version de TaxHub :

  ::

        cp -aR taxhub_old/static/medias/ taxhub/static/

* Lancer l'installation de l'application et de ses dépendances :

  ::

        cd taxhub
        ./install_app.sh

* Si vous utilisez TaxHub tout seul (sans GeoNature), mettre à jour le schéma de base de données en activant l'environnement virtuel :

  ::

        cd taxhub
        source venv/bin/activate
        flask db autoupgrade
        deactivate

* Une fois que l'installation est terminée et fonctionnelle, vous pouvez supprimer la version précédente de TaxHub (répertoire ``taxhub_old``).


Développement
=============

Pour lancer l'application en mode debug :

::

    $ cd ~/taxhub
    $ source venv/bin/activate
    $ flask run

TaxHub est alors accessible à l’adresse : ``http://localhost:5000`` (sans ``/taxhub``).
