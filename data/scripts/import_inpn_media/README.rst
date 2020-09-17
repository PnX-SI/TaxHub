
Script d'import des médias de l'INPN
====================================

| Exemple d'utilisation de la fonctionnalité importer des médias depuis l'INPN. 
| Ressources : `Connecter TaxHub à wikidata (ou l'INPN) pour en récupérer les médias <https://github.com/PnX-SI/TaxHub/issues/150>`_ 


Configuration
-------------

Modifier le fichier ``config.py``, en le créant à partir du fichier ``config.py.sample`` : ``cp config.py.sample config.py``

``SQLALCHEMY_DATABASE_URI`` = Chaine de connexion à la base de données

``QUERY_SELECT_CDREF`` = Requete SQL permettant de sélectionner les cd_ref


Installation
------------

* Dans un terminal, se placer dans le dossier du script puis créer l'environnement virtuel Python 3 :

::
   
   virtualenv -p /usr/bin/python3 venv
   # Alternative : python3 -m venv venv
   source venv/bin/activate
   pip install psycopg2
   pip install requests
   deactivate


Usage
-----

Lancer le script :

::
   
   source venv/bin/activate
   python import_inpn_media.py
   deactivate

Le script ajoute toutes les photos en tant que "Photo secondaire" (*id_type = 2*).

L'API de l'INPN ne permet pas encore (2020-09-01) d'obtenir les votes 
effectués sur les images sur le site de l'INPN. Cette information pourrait 
servir à sélectionner un photo principale (*id_type = 1*).

Si vous souhaitez malgré tout ajouter une photo principale vous pouvez en sélectionner 
une aléatoirement (ici le plus petit ``id_media`` pour chaque ``cd_ref``) :

.. code-block:: sql

   WITH first_media AS (
      SELECT MIN(id_media) AS first_id_media_founded, cd_ref 
      FROM taxonomie.t_medias
      GROUP BY cd_ref
   )
   UPDATE taxonomie.t_medias AS tm 
      SET id_type = 1
      FROM first_media AS fm
      WHERE tm.id_media = fm.first_id_media_founded
         AND tm.cd_ref = fm.cd_ref ;

Une fois l'import des médias effectué, et à fin de **rendre visible les photos sur GeoNature-atlas**, 
il est nécessaire de rafraichir les données de ses vues matérialisées *atlas.vm_medias* et *atlas.vm_taxons_plus_observes* : 

::

   REFRESH MATERIALIZED VIEW atlas.vm_medias WITH DATA ; 
   REFRESH MATERIALIZED VIEW atlas.vm_taxons_plus_observes WITH DATA ;


Dépendances
-----------

Ce script nécessite Python 3 et les bibliothèques suivantes (à installer via pip dans un virtualenv de préférence) :

- psycopg2
- requests
