=========
CHANGELOG
=========

1.1.3 (dev)
------------------

1.1.2 (2017-02-23)
------------------

**Changements**

- Correction du code pour compatibilité avec Angular 1.6.1
- Passage à npm pour la gestion des dépendances (librairies)
- Mise à jour du sous-module d'authentification
- Ajout de la liste des gymnospermes oubliés
- Création d'une liste ``Saisie possible``, remplaçant l'attribut ``Saisie``. Cela permet de choisir les synonymes que l'on peut saisir ou non dans GeoNature en se basant sur les ``cd_nom`` (``bib_listes`` et ``cor_nom_liste``) et non plus sur les ``cd_ref`` (``bib_attributs`` et ``cor_taxon_attribut``).
- Bugfix (cf #100)

**Note de version**

- Exécutez la procédure standard de mise à jour de l'application (http://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-lapplication)
- Si vous n'avez pas déjà fait ces modifications du schéma ``taxonomie`` depuis GeoNature (https://github.com/PnEcrins/GeoNature/blob/master/data/update_1.8.2to1.8.3.sql#L209-L225), éxécutez le script SQL de mise à jour de la BDD ``data/update1.1.1to1.1.2.sql``.
- Si vous ne l'avez pas fait côté GeoNature, vous pouvez supprimer l'attribut ``Saisie`` après avoir récupéré les informations dans la nouvelle liste avec ces lignes de SQL : https://github.com/PnEcrins/GeoNature/blob/master/data/update_1.8.2to1.8.3.sql#L307-L314
- Rajoutez le paramètre ``COOKIE_AUTORENEW = True`` dans le fichier ``config.py``.


1.1.1 (2016-12-14)
------------------

**Changements**

- Fixation et livraison des librairies suite à l'arrivée d'AngularJS1.6 (suppression du gestionnaire de dépendances bower)
- Mise à disposition des listes rouges (non encore utilisé dans l'application)

**Note de version**

- Exécutez la procédure standard de mise à jour de l'application (http://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-lapplication)
- Mettre à jour la base de données
	- Exécuter la commande suivante depuis la racine du projet TaxHub ``unzip data/inpn/LR_FRANCE.zip -d /tmp``
	- Exécuter le fichier ``data/update1.1.0to1.1.1.sql``


1.1.0 (2016-11-17)
------------------

**Changements**

- Bugfix
- Ajout d'un titre à l'application
- Gestion des null et des chaines vides
- Correction de l'installation
- Correction de l'effacement du type de média dans le tableau après enregistrement
- Ajout d'une clé étrangère manquante à la création de la base de données
- Ajout des listes rouges INPN (en base uniquement pour le moment)
- Compléments sur les attributs des taxons exemples
- Ajout d'une confirmation avant la suppression d'un media
- Champ ``auteur`` au lieu du champ ``description`` dans le tableau des médias
- Modification du type de données pour l'attribut ``milieu`` 
- Possibilité de choisir pour l''installation du schéma utilisateurs - local ou foreign
- Meilleure articulation et cohérence avec UsersHub GeoNature et GeoNature-atlas
- Amélioration en vue d'une installation simplifiée

1.0.0 (2016-09-06)
------------------

Première version fonctionnelle et déployable de Taxhub (Python Flask)

**Fonctionnalités**

- Visualisation de taxref
- Gestion du catalogue de noms d'une structure
- Association de données attributaires aux taxons d'une structure
- Association de médias aux taxons d'une structure

0.1.0 (2016-05-12)
------------------

**Première version de TaxHub développée avec le framework PHP Symfony**

Permet de lister le contenu de TaxRef, le contenu de ``taxonomie.bib_taxons``, de faire des recherches, d'ajouter un taxon à ``taxonomie.bib_taxons`` depuis TaxRef et d'y renseigner ses propres attributs.

L'ajout d'un taxon dans des listes n'est pas encore développé. 

Le MCD a été revu pour se baser sur ``taxonomie.bib_attributs`` et non plus sur les filtres de ``bib_taxons`` mais il reste encore à revoir le MCD pour ne pas pouvoir renseigner différemment les attributs d'un même taxon de référence - https://github.com/PnX-SI/TaxHub/issues/71

A suivre : Remplacement du framework Symfony (PHP) par Flask (Python) - https://github.com/PnX-SI/TaxHub/issues/70

0.0.1 (2015-04-01)
------------------

* Création du projet et de la documentation
