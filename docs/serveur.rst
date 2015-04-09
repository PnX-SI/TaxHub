.. image:: http://geotrek.fr/images/logo-pne.png
    :target: http://www.ecrins-parcnational.fr
    
=======
SERVEUR
=======


Prérequis
=========

* Ressources minimum serveur :

Un serveur disposant d'au moins de 1 Go RAM et de 10 Go d'espace disque.


* disposer d'un utilisateur linux nommé ``synthese``. Le répertoire de cet utilisateur ``synthese`` doit être dans ``/home/synthese``

    :: 
    
        sudo adduser --home /home/synthese synthese


* récupérer le zip de l'application sur le Github du projet

    ::
    
        cd /tmp
        wget https://github.com/PnEcrins/GeoNature/archive/vX.Y.Z.zip
        unzip vX.Y.Z.zip
        mkdir -p /home/synthese/geonature
        cp geonature-X.Y.Z/* /home/synthese/geonature
        cd /home/synthese


Installation et configuration du serveur
========================================

Installation pour Debian 7.

:notes:

    Cette documentation concerne une installation sur Debian. Pour tout autre environemment les commandes sont à adapter.