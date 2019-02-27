=========
CHANGELOG
=========

1.6.2 (2019-02-27)
------------------

**Nouveautés**

* Ajout du rang de l'espèce et du cd_nom sur l'API de recherche des taxons (autocomplete dans la table ``vm_taxref_list_forautocomplete``), utilisée par GeoNature

**Corrections**

* Ajout d'index uniques pour le rafraichissement des vues matérialisées
* Correction de l'index sur la table ``taxonomie.vm_taxref_list_forautocomplete`` pour le trigramme
* Centralisation des logs supervisor et gunicorn dans un seul fichier (``taxhub_path/var/log/``)

**Note de version**

* Afin que les logs de l'application (supervisor et gunicorn) soient tous écrits au même endroit, modifier le fichier ``taxhub-service.conf`` (``sudo nano /etc/supervisor/conf.d/taxhub-service.conf``). A la ligne ``stdout_logfile``, remplacer la ligne existante par : ``stdout_logfile = /home/<MON_USER>/taxhub/var/log/taxhub-errors.log`` (en remplaçant ``<MON_USER>`` par votre utilisateur linux)
* Pour ne pas avoir de conflits de sessiosn d'authentification entre TaxHub et GeoNature, ajouter une variable ``ID_APP`` dans le fichier de configuration ``config.py`` et y mettre l'identifiant de l'application TaxHub tel qu'il est inscrit dans la table ``utilisateurs.t_applications``. Exemple : ``ID_APP = 2``
* Exécuter le script de migration SQL: https://github.com/PnX-SI/TaxHub/blob/1.6.2/data/update1.6.1to1.6.2.sql
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.6.1 (2019-01-21)
------------------

**Corrections**

* Mise à jour de la version du sous-module d'authentification
* Mise à jour de SQLAlchemy
* Utilisation par défaut du mode d'authentification plus robuste (``hash``)
* Clarification des notes de version

**Notes de version**

* Si vous mettez à jour depuis la version 1.6.0, passez le paramètre ``PASS_METHOD`` à ``hash`` dans le fichier ``config.py``
* Vous pouvez passer directement à cette version, mais en suivant les notes de versions de chaque version
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.6.0 (2019-01-15)
------------------

**Nouveautés**

* Ajout et utilisation de l'extension PostgreSQL ``pg_tgrm`` permettant d'améliorer la pertinence de recherche d'une espèce au niveau de l'API d'autocomplétion de TaxHub, utilisée dans GeoNature, en utilisant l'algorithme des trigrammes (http://si.ecrins-parcnational.com/blog/2019-01-fuzzy-search-taxons.html)
* Suppression du SQL local du schéma ``utilisateurs`` pour utiliser celui du dépôt de UsersHub (#165)
* Compatibilité avec UsersHub V2 (nouvelles tables et vues de rétrocompatibilité)
* Ajout d'un taxon synonyme dans les données d'exemple

**Corrections**

* Import médias INPN - Prise en compte de l'import de photos de synonymes
* Corrections du manuel utilisateur (https://taxhub.readthedocs.io/fr/latest/manuel.html)
* Retour en arrière sur la configuration Apache et l'ajout du ServerName pour les redirections automatiques sans ``/`` mais précision dans la documentation : https://taxhub.readthedocs.io/fr/latest/installation.html#configuration-apache (#125)
* Correction des listes déroulantes à choix multiple pour afficher les valeurs et non les identifiants (par @DonovanMaillard)

**Notes de version**

* Exécuter la commande suivante pour ajouter l'extension PostgreSQL ``pg_trgm``, en remplaçant la variable ``$db_name`` par le nom de votre BDD : ``sudo -n -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"``
* Vous pouvez adapter la configuration Apache de TaxHub pour y intégrer la redirection sans ``/`` à la fin de l'URL (https://taxhub.readthedocs.io/fr/latest/installation.html#configuration-apache)
* Exécutez le script de mise de la BDD : https://raw.githubusercontent.com/PnX-SI/TaxHub/1.6.0/data/update1.5.1to1.6.0.sql
* Suivez la procédure habituelle de mise à jour de TaxHub: https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.5.1 (2018-10-17)
------------------

**Nouveautés**

* Script d'import des médias depuis l'API INPN (``data/scripts/import_inpn_media``)
* Création d'un manuel d'utilisation dans la documentation : https://taxhub.readthedocs.io/fr/latest/manuel.html (merci @DonovanMaillard)
* Amélioration de la configuration Apache pour que l'URL de TaxHub sans ``/`` à la fin redirige vers la version avec ``/`` (#125)

**Corrections**

* Remise à zéro des séquences

**Notes de versions**

* Suivez la procédure classique de mise à jour de TaxHub
* Exécutez le script de mise à jour de la BDD TaxHub ``data/update1.5.0to1.5.1.sql``


1.5.0 (2018-09-19)
------------------

**Nouveautés**

* Ajout de la possibilité de filtrer les attributs par ``id_theme`` ou ``id_attribut`` au niveau de la route ``taxoninfo``
* Ajout de routes pour récupérer ``bib_taxref_habitats`` et ``bib_taxref_categories_lr`` (listes rouges nationales)
* Installation : Ajout de paramètres permettant de mieux définir les données à intégrer et séparation des scripts SQL, notamment pour ne pas imposer d'intégrer toutes les données nécéessaires à GeoNature V1 (attributs et listes)
* Mise à jour de Flask (0.11.1 à 1.0.2), Jinja, psycopg2 et Werkzeug


1.4.1 (2018-08-20)
------------------

**Corrections**

* Correction de l'enregistrement lors du peuplement d'une liste


1.4.0 (2018-07-12)
------------------

**Nouveautés**

- Migration de Taxref 9 à 11 et scripts de migration (#155 et #156)
- Ajout d'un champ ``comments`` à la table ``bib_noms`` et dans le formulaire de saisie
- Passage du champ ``bib_noms.nom_francais`` en varchar(1000), du champ ``taxref.nom_vern`` en varchar(1000) et du champ ``taxref.lb_auteur`` en varchar(250)
- Amélioration des logs et mise en place d'une rotation des logs
- Création d'une fonction pour créer les répertoires système (``create_sys_dir()``)
- Amélioration de la vue permettant de rechercher un taxon (https://github.com/PnX-SI/GeoNature/issues/334)

**Note de version**

- Ajouter le mode d'authentification dans ``config.py`` (https://github.com/PnX-SI/TaxHub/blob/87fbb11d360488e97eef3a0bb68f566744c54aa6/config.py.sample#L25)
- Exécutez les scripts de migration de Taxref 9 à 11 (``data/scripts/update_taxref_v11/``) en suivant les indications de https://github.com/PnX-SI/TaxHub/issues/156
- Exécutez le script SQL de mise à jour de la BDD ``data/update1.3.2to1.4.0.sql``
- Suivez la procédure générique de mise à jour de l'application


1.3.2 (2017-12-15)
------------------

**Nouveautés**

- Optimisation du chargement des noms dans les listes
- Optimisation des requêtes
- Affichage du rang sur les fiches des taxons/noms
- Ajout d'un champ ``source`` et ``licence`` pour les médias (sans interface de saisie pour le moment). Voir #151, #126
- Script de récupération de médias depuis mediawiki-commons (expérimental). Voir #150
- Ajout d'un service de redimensionnement à la volée des images (http://URL_TAXHUB/api/tmedias/thumbnail/2241?h=400&w=600 où 2241 est l'id du média). Il est aussi possible de ne spécifier qu'une largeur ou une hauteur pour que l'image garde ses proportions sans ajouter de bandes noires. Voir #108
- Correction et compléments documentation (compatibilité Debian 9 notamment)
- Compatibilité avec Python 2

**Corrections**

- Ajout d'une liste vide impossible #148
- Enregistrement d'un attribut de type select (bug de la version 1.3.1, ce n'était pas la valeur qui était enregistrée mais l'index)
 
**Note de version**

- Vous pouvez directement passer de la version 1.1.2 à la 1.3.2 mais en suivant les différentes notes de version.
- Exécutez le script SQL de mise à jour de la BDD ``data/update1.3.1to1.3.2.sql``
- Suivez la procédure générique de mise à jour de l'application


1.3.1  (2017-09-26)
-------------------

**Corrections**

- Optimisation des performances pour le rafraichissement d'une vue matérialisée qui est devenue une table controlée (``vm_taxref_list_forautocomplete``) par trigger (``trg_refresh_mv_taxref_list_forautocomplete``). Voir #134
- Utilisation du nom francais de la table ``bib_noms`` pour la table ``vm_taxref_list_forautocomplete``. Cette table permet de stocker les noms sous la forme ``nom_vern|lb_nom = nom_valide`` pour les formulaires de recherche d'un taxon. 
- Dans la liste taxref, tous les noms étaient considérés comme nouveaux (plus de possibilité de modification)

**Note de version**

- Vous pouvez directement passer de la version 1.1.2 à la 1.3.1 mais en suivant les différentes notes de version.
- Exécutez le script SQL de mise à jour de la BDD ``data/update1.3.0to1.3.1.sql``


1.3.0  (2017-09-20)
-------------------

**Nouveautés**

- Ajout d'un trigger assurant l'unicité de la photo principale pour chaque cd_ref dans la table ``taxonomie.t_medias``. Si on ajoute une photo principale à un taxon qui en a déjà une, alors la précédente bascule en photo
- Performances dans les modules TaxRef et Taxons : au lieu de charger toutes les données côté client, on ne charge que les données présentes à l'écran et on lance une requête AJAX à chaque changement de page ou recherche
- Valeurs des listes déroulantes des attributs par ordre alphabétique
- Formulaire BIB_NOMS : Les champs ``nom latin``, ``auteur`` et ``cd_nom`` ne sont plus modifiables car ce sont des infos venant de TaxRef.
- Performances de la BDD : création d'index sur la table Taxref
- Suppression de Taxref du dépôt pour le télécharger sur http://geonature.fr/data/inpn/ lors de l'installation automatique de la BDD
- Ajout de nombreuses fonctions et vues matérialisées dans la BDD : https://github.com/PnX-SI/TaxHub/blob/develop/data/update1.2.0to1.3.0.sql
- Nettoyage et amélioration des routes de l'API

**Note de version**

- Exécutez le script SQL de mise à jour de la BDD ``data/update1.2.0to1.3.0.sql``
- Installer Python3 : ``sudo apt-get install python3``
- Installer Supervisor : ``sudo apt-get install supervisor``
- Compléter le fichier ``settings.ini`` avec les nouveaux paramètres sur la base de la version par défaut (https://github.com/PnX-SI/TaxHub/blob/master/settings.ini.sample)
- Supprimer le paramètre ``nb_results_limit`` du fichier ``static/app/constants.js`` (voir https://github.com/PnX-SI/TaxHub/blob/master/static/app/constants.js.sample)
- Arrêter le serveur HTTP Gunicorn : ``make prod-stop``
- Lancer le script d'installation : ``./install_app.sh``
- Vous pouvez directement passer de la version 1.1.2 à la 1.3.0 mais en suivant les notes de version de la 1.2.0.  


1.2.1 (2017-07-04)
------------------

**Nouveautés**

- Correction de la conf Apache pour un accès à l'application sans le slash final dans l'URL
- Retrait du "v" dans le tag de la release

**Note de version**

- Vous pouvez directement passer de la version 1.1.2 à la 1.2.1 mais en suivant les notes de version de la 1.2.0. 


1.2.0 (2017-06-21)
------------------

**Nouveautés**

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

- Exécutez le script SQL de mise à jour de la BDD ``data/update1.1.2to1.2.0.sql``.
- Exécutez le script install_app.sh qui permet l'installation de gunicorn et la mise à jour des dépendances python et javascript.

:Attention:

    TaxHub n'utilise plus wsgi mais un serveur HTTP python nommé ``Gunicorn``. Il est nécessaire de revoir la configuration Apache et de lancer le serveur http Gunicorn

* Activer le mode proxy de Apache
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

* Si vous voulez arrêter le serveur HTTP Gunicorn :
::

	make prod-stop
		
L'application doit être disponible à l'adresse http://monserver.ext/taxhub


1.1.2 (2017-02-23)
------------------

**Nouveautés**

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

**Nouveautés**

- Fixation et livraison des librairies suite à l'arrivée d'AngularJS1.6 (suppression du gestionnaire de dépendances bower)
- Mise à disposition des listes rouges (non encore utilisé dans l'application)

**Note de version**

- Exécutez la procédure standard de mise à jour de l'application (http://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application)
- Mettre à jour la base de données
 * Exécuter la commande suivante depuis la racine du projet TaxHub ``unzip data/inpn/LR_FRANCE.zip -d /tmp``
 * Exécuter le fichier ``data/update1.1.0to1.1.1.sql``


1.1.0 (2016-11-17)
------------------

**Nouveautés**

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

**Première version de TaxHub, développée avec le framework PHP Symfony**

Permet de lister le contenu de TaxRef, le contenu de ``taxonomie.bib_taxons``, de faire des recherches, d'ajouter un taxon à ``taxonomie.bib_taxons`` depuis TaxRef et d'y renseigner ses propres attributs.

L'ajout d'un taxon dans des listes n'est pas encore développé. 

Le MCD a été revu pour se baser sur ``taxonomie.bib_attributs`` et non plus sur les filtres de ``bib_taxons`` mais il reste encore à revoir le MCD pour ne pas pouvoir renseigner différemment les attributs d'un même taxon de référence - https://github.com/PnX-SI/TaxHub/issues/71

A suivre : Remplacement du framework Symfony (PHP) par Flask (Python) - https://github.com/PnX-SI/TaxHub/issues/70


0.0.1 (2015-04-01)
------------------

* Création du projet et de la documentation
