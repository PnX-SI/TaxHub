===========
APPLICATION
===========

Prérequis
=========

* Environnement serveur :

Voir le guide d'installation du serveur dans https://github.com/PnX-SI/TaxHub/blob/master/docs/serveur.rst

* Cet documentation présente la procédure avec un utilisateur linux nommé ``synthese``. Dans ce guide, le répertoire de cet utilisateur est dans ``/home/synthese``. Adapter les chemins selon votre serveur.

* Se loguer sur le serveur avec l'utilisateur ``synthese`` ou tout autre utilisateur linux faisant partie du groupe www-data.

* Récupérer le zip de l’application sur le Github du projet (`X.Y.Z à remplacer par le numéro de version souhaitée <https://github.com/PnX-SI/TaxHub/releases>`_), dézippez le dans le répertoire ``/home/synthese`` :

  ::  
  
        cd /home/synthese
        wget https://github.com/PnX-SI/TaxHub/archive/X.Y.Z.zip
        unzip X.Y.Z.zip
        mv TaxHub-X.Y.Z/ taxhub/


Configuration initiale
======================

Si Python 3 n'est pas déjà installé sur le serveur :

::

    sudo apt-get install python3

* Créer et mettre à jour le fichier ``settings.ini``
 
  ::  
  
        cd taxhub
        cp settings.ini.sample settings.ini
        nano settings.ini

Renseigner les informations nécessaires à la connexion à la base de données PostgreSQL. Il est possible mais non conseillé de laisser les valeurs proposées par défaut. 

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh`` et par le script ``install_app.sh``. 

Les utilisateurs PostgreSQL doivent être en concordance avec ceux créés lors de la dernière étape de l'installation serveur ``Création de 2 utilisateurs PostgreSQL``. 

Configuration Apache
====================

* Voici une des manières de configurer Apache via le fichier ``/etc/apache2/sites-available/000-default.conf``. Vous pouvez aussi créer un virtualhost dédié à l'application.

Créer le fichier de configuration Apache ``taxhub.conf`` dans ``/etc/apache2/sites-availables/`` :

::

    sudo nano /etc/apache2/sites-available/taxhub.conf
    
Rajouter les informations suivantes

::

    # Configuration TaxHub
      <Location /taxhub>
        ProxyPass  http://127.0.0.1:5000/ retry=0
        ProxyPassReverse  http://127.0.0.1:5000/
      </Location> 
    #FIN Configuration TaxHub

Si vous souhaitez que TaxHub soit accessible sans slash à la fin, par exemple sur http://mondomaine.fr/taxhub, ajoutez ces 2 lignes dans le Virtualhost du fichier ``/etc/apache2/sites-available/000-default.conf`` :

::

    RewriteEngine  on
    RewriteRule    "taxhub$"  "taxhub/"  [R]

* Activer les modules, le nouvel hote virtuel et redémarrer Apache
 
  ::  
  
        sudo a2enmod proxy
        sudo a2enmod proxy_http
        sudo a2enmod rewrite
        sudo a2ensite taxhub.conf
        sudo apache2ctl restart



Création de la base de données
==============================

* Lancer le fichier d'installation et de préparation de la base de données
 
  ::  
  
        cd /home/synthese/taxhub
        sudo ./install_db.sh

:notes:

    En cas d'erreur : ``could not change directory to "/home/synthese/taxhub": Permission non accordée``, assurez vous que les répertoires ``taxhub`` et ``data/inpn`` aient bien des doits d'execution pour les utilisateurs 'autres'
  

Installation de l'application
=============================

* Lancer le fichier d'installation et de configuration de l'application
 
  ::  
  
        ./install_app.sh

* Tester l'accès à l'application : http://mondomaine.fr/taxhub

        
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
  
        cd /home/synthese/
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
