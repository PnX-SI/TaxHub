TaxHub
=========

Application web de gestion centralisée des taxons basée sur le référentiel TAXREF (http://inpn.mnhn.fr/programme/referentiel-taxonomique-taxref) du MNHN. 

Elle permet de gérer la liste des taxons présents dans chaque structure, d'y greffer des informations spécifiques, de définir des listes de taxons et des filtres en fonction des besoins. 

Elle est utilisée pour la structuration des taxons dans https://github.com/PnEcrins/GeoNature (à partir de sa version 1.4.0).

.. image :: docs/images/taxref-liste.jpg

.. image :: docs/images/detail-taxon.jpg

Principes
=========

Voici le modèle conceptuel de la base de données de TaxHub :

.. image :: https://cloud.githubusercontent.com/assets/4418840/7047406/9d39134a-de0c-11e4-97fa-ff37323d20e7.jpg

La partie en VERT correspond au TAXREF complet tel que fourni par le MNHN. Son contenu ne doit pas être modifié.

La partie en ROSE correspond à la partie spécifique à chaque structure. Il faut commencer par renseigner la table `bib_taxons` en selectionnant les taxons qui nous intéressent dans le TAXREF. 

Il faut ensuite y greffer des informations spécifiques grace à `bib_attributs` (patrimonialité, marqueurs, autres selon les besoins), définir des sous-listes de taxons (amphibiens, ....) dans `bib_listes` et définir des filtres grace à `bib_filters` en fonction des besoins.

Technologies
------------

- Langages : Python, HTML, JS, CSS
- BDD : PostgreSQL, PostGIS
- Serveur : Debian ou Ubuntu
- Framework python : flask
- Framework JS : AngularJS
- Framework CSS : Bootstrap

Auteurs
-------

- Amandine Sahl
- Gil Deluermoz
- Damien Frazzoni
- Claire Lagaye
- Christophe Chillet
- Samuel Priou
- Thomas Lebard
- Camille Monchicourt

License
-------

* OpenSource - GPL V3
* Copyright (c) 2014-2015 - Parc National des Écrins - Parc national des Cévennes


.. image:: http://pnecrins.github.io/GeoNature/img/logo-pne.jpg
    :target: http://www.ecrins-parcnational.fr

.. image:: http://pnecrins.github.io/GeoNature/img/logo-pnc.jpg
    :target: http://www.cevennes-parcnational.fr

