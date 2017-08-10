=========
CHANGELOG
=========


1.3.0 dev (unrelease)
------------------

**Changements**

- Ajout d'un trigger assurant l'unicité de la photo principale dans la table ``taxonomie.t_medias``


1.2.1 (2017-07-04)
------------------

**Changements**

- Correction de la conf apache pour un accès à l'application sans le slashe final dans l'URL
- Retrait du "v" dans le tag de la release

**Note de version**

* Vous pouvez directement passer de la version 1.1.2 à la 1.2.1 mais en suivant les notes de version de la 1.2.0. 


1.2.0 (2017-06-21)
------------------

**Changements**

- Ajout de toutes les fonctionnalités de gestion des listes ainsi que des noms de taxons qu'elles peuvent contenir.
- Possibilité d'exporter le contenu d'une liste de noms en CSV.
- Correction du fonctionnement de la pagination.
- Permettre la validation du formulaire d'authentification avec la touche ``Entrer``.
- Bib_noms : ajout de la possibilité de gérer le multiselect des attributs par checkboxs.
- Utilisation de gunicorn comme serveur http et mise en place d'un makefile.
- Suppression du sous-module d'authentification en tant que sous module git et intégration de ce dernier en tant que module python.
- Mise à jour de la lib psycopg2.
- Installation : passage des requirements en https pour les firewall.

**Note de version**

* Exécutez le script SQL de mise à jour de la BDD ``data/update1.1.2to1.2.0.sql``.
* Exécutez le script install_app.sh qui permet l'installation de gunicorn et la mise à jour des dépendances python et javascript.

:Attention:

    TaxHub n'utilise plus wsgi mais un serveur HTTP python nommé ``Gunicorn``. Il est nécessaire de revoir la configuration Apache et de lancer le serveur http Gunicorn

* Activer le mode proxy de apache
::

	sudo a2enmod proxy
	sudo a2enmod proxy_http
	sudo apache2ctl restart
		
* Supprimer la totalité de la configuration Apache concernant TaxHub et remplacez-la par celle-ci :
::
  
	# Configuration TaxHub
		<Location /taxhub>
			ProxyPass  http://127.0.0.1:8000/
			ProxyPassReverse  http://127.0.0.1:8000/
		</Location>
	# FIN Configuration TaxHub

* Redémarrer Apache : 
::

	sudo service apache2 restart
	
* Lancer le serveur HTTP Gunicorn :
::

	make prod

* Arrêter le serveur HTTP Gunicorn :
::

	make prod-stop
		
L'application doit être disponible à l'adresse http://monserver.ext/taxhub


1.1.2 (2017-02-23)
------------------

**Changements**

- Correction du code pour compatibilité avec Angular 1.6.1.
- Passage à npm pour la gestion des dépendances (librairies).
- Mise à jour du sous-module d'authentification.
- Ajout de la liste des gymnospermes oubliés.
- Création d'une liste ``Saisie possible``, remplaçant l'attribut ``Saisie``. Cela permet de choisir les synonymes que l'on peut saisir ou non dans GeoNature en se basant sur les ``cd_nom`` (``bib_listes`` et ``cor_nom_liste``) et non plus sur les ``cd_ref`` (``bib_attributs`` et ``cor_taxon_attribut``).
- Création d'une documentation standard de mise à jour de l'application.
- Bugfix (cf https://github.com/PnX-SI/TaxHub/issues/100).

**Note de version**

- Exécutez la procédure standard de mise à jour de l'application (http://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application)
- Si vous n'avez pas déjà fait ces modifications du schéma ``taxonomie`` depuis GeoNature (https://github.com/PnEcrins/GeoNature/blob/master/data/update_1.8.2to1.8.3.sql#L209-L225), exécutez le script SQL de mise à jour de la BDD ``data/update1.1.1to1.1.2.sql``.
- Si vous ne l'avez pas fait côté GeoNature, vous pouvez supprimer l'attribut ``Saisie`` après avoir récupéré les informations dans la nouvelle liste avec ces lignes de SQL : https://github.com/PnEcrins/GeoNature/blob/master/data/update_1.8.2to1.8.3.sql#L307-L314
- Rajoutez le paramètre ``COOKIE_AUTORENEW = True`` dans le fichier ``config.py``.


1.1.1 (2016-12-14)
------------------

**Changements**

- Fixation et livraison des librairies suite à l'arrivée d'AngularJS1.6 (suppression du gestionnaire de dépendances bower)
- Mise à disposition des listes rouges (non encore utilisé dans l'application)

**Note de version**

- Exécutez la procédure standard de mise à jour de l'application (http://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application)
- Mettre à jour la base de données
	- Exécuter la commande suivante depuis la racine du projet TaxHub ``unzip data/inpn/LR_FRANCE.zip -d /tmp``
	- Exécuter le fichier ``data/update1.1.0to1.1.1.sql``


1.1.0 (2016-11-17)
------------------

**Changements**

- Bugfix
- Ajout d'un titre à l'application
- Gestion des valeurs ``null`` et des chaines vides
- Correction de l'installation
- Correction de l'effacement du type de média dans le tableau après enregistrement
- Ajout d'une clé étrangère manquante à la création de la base de données
- Ajout des listes rouges INPN (en BDD uniquement pour le moment)
- Compléments sur les attributs des taxons exemples
- Ajout d'une confirmation avant la suppression d'un media
- Champ ``auteur`` affiché au lieu du champ ``description`` dans le tableau des médias
- Modification du type de données pour l'attribut ``milieu`` 
- Possibilité de choisir pour l'installation du schéma ``utilisateurs`` - en local ou en Foreign Data Wrapper
- Meilleure articulation et cohérence avec UsersHub, GeoNature et GeoNature-atlas
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
