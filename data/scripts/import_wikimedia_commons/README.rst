Ce script permet d'importer les médias Commons à partir des cd_noms présents dans Wikidata. 

Pour en savoir plus : https://github.com/PnX-SI/TaxHub/issues/150

Installation de l'environnement Python
--------------------------------------

- Pour être plus propre il est conseillé de créer un nouveau virtualenv et d'y installer les paquets Python

::

    virtualenv -p /usr/bin/python3 venv #Python 3 n'est pas requis
    source venv/bin/activate
    pip install lxml psycopg2 requests SPARQLWrapper xmltodict
    deactivate

Configuration du script
-----------------------

- Paramètres de connexion à la BDD : 

Pour récupérer les paramètres de connexion à TaxHub, créer un lien symbolique ``config.py`` : 

::
    
    ln -s  ../../../config.py .
    
Vous pouvez aussi définir votre propre connexion : 

- Sélection d'une liste de ``cd_ref``. Trois requêtes d'exemple figurent dans le script :
  
  - liste des ``cd_ref`` des taxons n'ayant pas de média
  - 10 premiers ``cd_ref`` de ``bib_noms`` (activé par défaut)
  - 100 premiers ``cd_ref`` de la table ``vm_taxons_plus_observes``

- Configuration du type de média que vous souhaitez récupérer
::
    
    WD_MEDIA_PROP # code de la propriété wikidata
    TAXHUB_MEDIA_ID_TYPE # Identifiant du type de média


- Paramétrage de la fonction ``main`` : 
  
  - connexion à la base de données
  - liste des ``cd_ref``
  - rafraichir les tables de l'atlas (True/False)
  - simulé l'insertion (True/False)

Execution du script
-------------------

- Activer le virtualenv :

::
    
    source venv/bin/activate

- lancer le script : 

::
    
    python run_import.py > import_mediawiki.log
