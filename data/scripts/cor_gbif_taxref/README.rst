Script d'import des correspondances entre Taxref et Identifiants de taxons GBIF
===============================================================================

| Exemple d'utilisation de la fonctionnalité importer les correspondances entre les cd_noms du taxref et les identifiants de taxons GBIF 


Configuration
-------------

A partir du fichier config.py.example, créer un fichier de configuration pour le script : 

::
    
    cp config.py.example config.py


Adaptez ce fichier de configuration en personnalisant vos paramètres de connexion à la base de données, et la requête permettant de sélectionner les 
cd_noms pour lesquels vous recherchez des correspondances GBIF.


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
   python get_cor_gbif_taxref.py
   deactivate

Le script permet de créer et alimenter une table de correspondances entre les cd_noms présents dans la version du taxref actuellement disponible 
dans la base de données, et l'identifiant ``taxon_key`` du taxon par le GBIF. Cette correspondance est récupérée via l'API de taxref.


Mise à jour des correspondances
-------------------------------

Lors d'une mise à jour de taxref ou si vous souhaitez modifier les cd_noms pour lesquels vous souhaitez récupérer les correspondances, vous pouvez relancer le 
script comme précédemment. Il vous sera alors demandé si vous souhaitez - ou non - annuler et remplacer les correspondances existantes.


Dépendances
-----------

Ce script nécessite Python 3 et les bibliothèques suivantes (à installer via pip dans un virtualenv de préférence) :

- psycopg2
- requests
