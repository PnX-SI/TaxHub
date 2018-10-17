
Exemple d'utilisation de la fonctionnalité importer médias depuis INPN

Configuration
=============

Modifier le fichier ``config.py``, en le créant à partir du fichier ``config.py.sample``

``SQLALCHEMY_DATABASE_URI`` = Chaine de connexion à la base de données

``QUERY_SELECT_CDREF`` = Requete SQL permettant de sélectionner les cd_ref


Usage
=====

* Créer environnement Python :

::
   
   virtualenv -p /usr/bin/python3 venv
   source venv/bin/activate
   pip install psycopg2
   pip install requests
   deactivate

* Lancer le script :

::
   
   source venv/bin/activate
   python import_inpn_media.py
   deactivate

Librairies requises (à installer via pip dans un virtualenv de préférence) :

- psycopg2
- requests
