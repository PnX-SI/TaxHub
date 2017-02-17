=========
CHANGELOG
=========

1.1.2 (dev)
------------------

**Changements**

- Correction du code pour compatibilité avec angular 1.6
- Passage à npm pour la gestion des librairies
- Mise à jour du sous module d'authentification
- Ajout de la liste des gymnospermes oubliés
- Bugfix (cf #100)

**Note de version**

- Avant de supprimer l'ancienne release
	- sauvegardez votre fichier settings.ini 
	- sauvegardez votre fichier static/app/constants.js
- Une fois la release 1.1.2 mise en place sur votre serveur
	- restaurez votre fichier ``settings.ini``. IMPORTANT : assurez vous que le paramètre ``drop_apps_db`` est bien égal à ```false``
	- exécutez le fichier ``install_app.sh``
	- restaurez votre fichier ``static/app/constants.js``
- Mettre à jour la base de données
	- exécuter le fichier ``update1.1.1to1.1.2.sql``


1.1.1 (2016-12-14)
------------------

**Changements**

- Fixation et livraison des librairies suite à l'arrivée d'AngularJS1.6 (suppression du gestionnaire de dépendances bower)
- mise à disposition des listes rouges (non encore utilisé dans l'application)

**Note de version**

- Avant de supprimer l'ancienne release
	- sauvegardez votre fichier settings.ini 
	- sauvegardez votre fichier static/app/constants.js
- Une fois la release 1.1.2 mise en place sur votre serveur
	- restaurez votre fichier ``settings.ini``. IMPORTANT : assurez vous que le paramètre ``drop_apps_db`` est bien égal à ```false``
	- exécutez le fichier ``install_app.sh``
	- restaurez votre fichier ``static/app/constants.js``
- Mettre à jour la base de données
	-exécuter la commande suivante de puis la racine du projet TaxHub ``unzip data/inpn/LR_FRANCE.zip -d /tmp``
	- exécuter le fichier ``update1.1.0to1.1.1.sql``


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
