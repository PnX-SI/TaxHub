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
        wget https://github.com/PnX-SI/TaxHub/archive/vX.Y.Z.zip
        unzip vX.Y.Z.zip
        mv TaxHub-X.Y.Z/ taxhub/

Configuration initiale
======================

* créer et mettre à jour le fichier ``settings.ini``

    :: 
    
        cd taxhub
        cp settings.ini.sample settings.ini
        nano settings.ini

Renseigner les informations nécessaires à la connexion à la base de données PostgreSQL. Il est possible mais non conseillé de laisser les valeurs proposées par défaut. 

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh``. Les utilisateurs PostgreSQL doivent être en concordance avec ceux créés lors de la dernière étape de l'installation serveur ``Création de 2 utilisateurs PostgreSQL``. 


Création de la base de données
==============================

todo

    
Installation de l'application
=============================

* Lancer le fichier d'installation et de préparation de la configuration de l'application

    ::
    
        cd /home/synthese/taxhub
        sudo ./install.sh


