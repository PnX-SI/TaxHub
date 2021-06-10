===========
APPLICATION
===========

Prérequis
=========

* Cet documentation présente la procédure avec un utilisateur linux nommé ``synthese``. Dans ce guide, le répertoire de cet utilisateur est dans ``/home/synthese``. Adapter les chemins selon votre serveur.

* Se loguer sur le serveur avec l'utilisateur ``synthese`` ou tout autre utilisateur linux faisant partie du groupe  ``www-data`` et  ``sudo``

* Savoir utiliser ``nano`` pour editer et sauvegarder des fichiers. Si vous ne savez pas comment faire, suivez ce tutoriel: https://openclassrooms.com/fr/courses/43538-reprenez-le-controle-a-laide-de-linux/39267-nano-lediteur-de-texte-du-debutant

**Voir le guide d'installation du serveur** dans https://github.com/PnX-SI/TaxHub/blob/master/docs/serveur.rst, qui contient notamment la phase de l'utilisation de l'utilisatur ``synthese`` mais aussi l'installation de dépendances importantes et la configuration de la base de données.

Récupération du code source
=============================

Récupérer le zip de l’application sur le Github du projet (`X.Y.Z à remplacer par le numéro de version souhaitée <https://github.com/PnX-SI/TaxHub/releases>`_), dézippez le dans le répertoire ``/home/synthese`` :

  .. code-block:: bash

    cd /home/synthese
    wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
    unzip X.Y.Z.zip
    mv TaxHub-X.Y.Z/ taxhub/
    rm X.Y.Z.zip
    cd taxhub

Exemple pour la version 1.6.5:

  .. code-block:: bash

    cd /home/synthese
    wget https://github.com/PnX-SI/TaxHub/archive/1.6.5.zip
    unzip 1.6.5.zip
    mv TaxHub-1.6.5/ taxhub/
    rm 1.6.5
    cd taxhub


Configuration initiale
======================

* Créer et mettre à jour le fichier ``settings.ini``:

  .. code-block:: bash

    cp settings.ini.sample settings.ini
    nano settings.ini

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh`` et par le script ``install_app.sh``.

Renseignez les informations nécessaires à la connexion à la base de données PostgreSQL. Il est possible de laisser la plupart des valeurs proposées par défaut, mais lisez au moins le fichier de bout en bout pour savoir ce qu'il est possible de changer.

La valeur la plus importante à mettre à jour est:

::

  user_pg_pass=monpassachanger

``monpassachanger`` doit être remplacé par la celui choisi lors de la dernière étape de l'installation serveur ``Création de 2 utilisateurs PostgreSQL``.

Stockage des media
------------------

Les media associés aux taxons peuvent être stockés sur le serveur (paramètre ``UPLOAD_FOLDER``) ou sur un cloud S3. Dans les deux cas, les miniatures sont stockées sur le serveur, dans ``UPLOAD_FOLDER``.
OVH propose une offre `Object storage <https://www.ovhcloud.com/fr/public-cloud/object-storage/>`_ compatible. `Voir ici <https://fabien.io/get-s3-credentials-ovh-public-cloud/>`_ la manipulation pour obtenir les identifants à renseigner dans le fichier de configuration (``S3_KEY`` et ``S3_SECRET``).
Pour utiliser votre propre sous-domaine (paramètre ``S3_PUBLIC_URL``) (ex : http://media.ADRESSE_DU_SERVEUR/taxons/image.jpg) : `<https://docs.ovh.com/gb/en/storage/pcs/link-domain/>_`

Configuration Apache
====================

Voici une des manières de configurer Apache. Elle se base sur le fait que la configuration ``/etc/apache2/sites-available/000-default.conf`` existe par défaut et va automatiquement charger notre nouvelle entrée. Elle vous permettra d'accéder à taxhub via l'url http://ADRESSE_DU_SERVEUR/taxhub.

Vous pourriez à la place créer un virtualhost dédié à l'application, mais c'est un cas d'usage avancé que nous ne convrirons pas.

Créer le fichier de configuration Apache ``taxhub.conf`` dans ``/etc/apache2/sites-availables/`` :

.. code-block:: bash

  sudo nano /etc/apache2/sites-available/taxhub.conf

Rajouter les informations suivantes:

::

  # Configuration TaxHub
  <Location /taxhub>
    ProxyPass  http://127.0.0.1:5000/ retry=0
    ProxyPassReverse  http://127.0.0.1:5000/
  </Location>

  Alias "/static" "/home/synthese/taxhub/static"
  <Directory "/home/synthese/taxhub/static">
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>
  #FIN Configuration TaxHub


Si vous souhaitez que TaxHub soit accessible sans slash à la fin, par exemple sur http://ADRESSE_DU_SERVEUR/taxhub, ajoutez ces 2 lignes dans le Virtualhost du fichier ``/etc/apache2/sites-available/000-default.conf`` :

::

  RewriteEngine  on
  RewriteRule    "taxhub$"  "taxhub/"  [R]

* Activer les modules, le nouvel hote virtuel et redémarrer Apache

.. code-block:: bash

  sudo a2ensite taxhub.conf
  sudo systemctl reload apache


Remplissage de la base de données
==============================

Lanceé le fichier d'installation et de préparation de la base de données

.. code-block:: bash

  cd /home/synthese/taxhub
  ./install_db.sh

Le script va ouvrir une nouvelle fois le fichier de configuration settings.ini avec nano, pour vous donner une opportunité de revoir une dernière fois ces paramètres. Vous pouvez sauvegarder le fichier tel quel pour continuer.

:notes:

  En cas d'erreur : ``could not change directory to "/home/synthese/taxhub": Permission non accordée``, assurez vous que les répertoires ``taxhub`` et ``data/inpn`` aient bien des doits d'execution pour les utilisateurs 'autres'


Installation de l'application
=============================

Lancez le fichier d'installation et de configuration de l'application

.. code-block:: bash

  ./install_app.sh

Tester l'accès à l'application en vous rendant sur http://ADRESSE_DU_SERVEUR/taxhub. Pour trouver l'adresse du serveur, faite:

.. code-block:: bash

  curl https://ipinfo.io/ip


Arrêter/Lancer l'application
=============================

* Pour arrêter TaxHub
  ::

         sudo supervisorctl stop taxhub

* Pour démarrer TaxHub
  ::

        sudo supervisorctl start taxhub


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
        cp taxhub_old/config.py taxhub/config.py
        cp taxhub_old/static/app/constants.js taxhub/static/app/constants.js

* Récupérer les médias uploadés dans la précédente version de TaxHub :

  ::

        cp -aR taxhub_old/static/medias/ taxhub/static/

* Lancer l'installation de l'application et de ses dépendances :

  ::

        cd taxhub
        ./install_app.sh

* Une fois que l'installation est terminée et fonctionnelle, vous pouvez supprimer la version précédente de TaxHub (répertoire ``taxhub_old``).


Développement
=============================
Pour lancer l'application en mode debug

::

    cd ~/taxhub
    make develop
