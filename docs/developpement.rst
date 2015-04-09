=============
DEVELOPPEMENT
=============

Cette rubrique est destinée aux développeurs qui souhaiteraient...


Routes Symfony
--------------

Pour avoir toutes les routes à jour, il suffit dans symfony de lancer la commande
::

    php app/console router:debug

Aujourd'hui les différentes routes générées par symfony sont

* /taxref/
    * Remonte toutes les données de la table taxonomie.taxref
    * Méthode autorisée : GET
    * Paramètres autorisés : Limit, Page pour paginer les résultats
* /taxref/{id}
    * Remonte un enregistrement de la table taxonomie.taxref
    * Méthode autorisée : GET
    * Paramètre: l'id de l'enregistrement
* /taxref/distinct/{field}
    * Remonte un distinct de la table taxonomie.taxref sur un champ spécifié
    * Méthode autorisée : GET
    * Paramètre obligatoire : le champ du distinct (n'importe quel champ de la table taxref)
    * Paramèter facultatif : un ou plusieurs critères (sur un ou plusieurs champs de la table)
    * Exemples
        - /taxref/distinct/phylum : remonte tous les phylum de la table
        - /taxref/distinct/famille?regne=Plantae&ordre=Rosales : remonte les familles du regne Plantae et de l'ordre Rosales
* /bibtaxons/ 
    * Remonte toutes les données de la table taxonomie.bib_taxons
    * Méthode autorisée : GET
* /bibtaxons/taxonomie
    * Remonte cd_nom, cd_taxsup, lb_nom et id_rang pour les familles, ordre, classe, phylum et regne des enregistrements de la table taxonomie.bibtaxons
    * Méthode autorisée : GET
* /bibtaxons/{id}
    * Remonte un enregistrement de la table taxonomie.bib_taxons
    * Méthode autorisée : GET
    * Paramètre: l'id de l'enregistrement
* /bibtaxons/{id} 
    * Création ou mise à jour d'un enregistrement dans la table taxonomie.bib_taxons
    * Méthode autorisée : POST|PUT
    * Paramètre: l'id de l'enregistrement (si update) ou rien (si create)
* /bibtaxons/{id} 
    * SUppression d'un enregistrement dans la table taxonomie.bib_taxons
    * Méthode autorisée : DELETE
    * Paramètre: l'id de l'enregistrement à supprimer
* /bibfiltres/
    * Remonte toutes les données de la table taxonomie.bib_filtres
    * Méthode autorisée : GET
* /bibfiltres/{id}
    * Remonte un enregistrement de la table taxonomie.bib_filtres
    * Méthode autorisée : GET
    * Paramètre: l'id de l'enregistrement


Bla bla bla
-----------

The most minimal components required to run an instance are :

* PostGIS 2 server
* GDAL, GEOS, libproj
* gettext
* libfreetype
* libxml2, libxslt
* Usual Python dev stuff

A voir : `the list of minimal packages on Debian/Ubuntu <https://github.com/makinacorpus/Geotrek/blob/211cd/install.sh#L136-L148>`_.

.. note::

    En lancant ``env_dev`` et ``update`` is recommended after a pull of new source code,
    but is not mandatory : ``make serve`` is enough most of the time.
