=========
CHANGELOG
=========

1.10.8 (unreleased)
-------------------

**🚀 Nouveautés**

* Le paramètre ``--keep-cdnom`` des scripts de migration de Taxref garde désormais tous les cd_nom supprimés dans la nouvelle version de Taxref, et plus seulement ceux présents dans la table ``bib_noms`` (#362)
* Ajout d'un clé primaire sur la table ``taxonomie.import_taxref`` pour accélérer les migrations de Taxref (364)
* Suppression des tables des anciens statuts de protections:
  * taxref_liste_rouge_fr
  * bib_taxref_categories_lr
  * taxref_protection_especes
  * taxref_protection_articles_structure
  * taxref_protection_articles

**🐛 Corrections**

* Gestion des cd_nom négatifs (#357)
* Ajout d'index sur ``vm vm_taxref_list_forautocomplete`` pour en améliorer les performances qui avaient été supprimés par errur dans la version 1.10.3 (#355)
* Correction d'un code de département dans la commande ``populate_bdc_statut_cor_text_area``
* Correction des scripts de migration de Taxref dans le cas des merges où plus de 2 grappes de cd_nom fusionnent (#365)
* Correction de l'encodage de la BDC statuts lors de la migration de Taxref (#361)

**💻 Développement**

* Mise à jour de la version de Node.js (et de la version de npm) en utilisant la LTS (version 18 actuellement) dans le fichier ``.nvmvrc``, et non plus la version 10 (#353)
* Mise à jour des actions Github (#356)

**⚠️ Notes de version**
* Si vous mettez à jour TaxHub, s'assurer qu'il n'y ait pas de vues qui dépendent des tables supprimées.
* Suite à la correction d'un code de département, il est fortement conseillé de relancer le peuplement des données de la table ``bdc_statut_cor_text_area`` en utilisant la commande suivante : 

  ::

    cd ~/taxhub
    source venv/bin/activate
    flask taxref link-bdc-statut-to-areas

1.10.7 (2022-12-20)
-------------------

**🐛 Corrections**

* Correction du bug dans la commande ``flask taxref link-bdc-statut-to-areas``
* Correction du message de confirmation de la commande ``flask taxref delete-bdc``


1.10.6 (2022-12-14)
-------------------

**🐛 Corrections**

* Mise à jour de UsersHub-authentification-module en version 1.6.2


1.10.5 (2022-12-13)
-------------------

**🚀 Nouveautés**

* Ajout de commandes permettant de gérer la base de connaissance du SINP des statuts des espèces :

  * ``flask taxref import-bdc-v14`` : utile si vous avez appelez ``import-v14`` avec ``--skip-bdc-statuts``
  * ``flask taxref import-bdc-v15`` : utile si vous avez appelez ``import-v15`` avec ``--skip-bdc-statuts``
  * ``flask taxref delete-bdc`` : permet de vider les tables de la BDC Statuts
  * ``flask taxref link-bdc-statut-to-areas`` : permet de peupler la table ``bdc_statut_cor_text_area``; utile si vous avez importé votre BDC Statuts avec TaxHub ≤ 1.10.4

* Mise à jour de UsersHub-authentification-module en version 1.6.2
* Les doublons ont été supprimés des données source de la BDC Statuts afin d’éviter cette lente opération lors de l’intégration dans la base de données.
* Les données des départements, nécessaires à la BDC Statuts, sont importées par défaut
* Les références à l’``ID_APP`` sont supprimées au profit du ``CODE_APPLICATION`` (``TH`` par défaut)
* Le dossier des fichiers statiques peut être défini avec la variable d’environnement ``TAXHUB_STATIC_FOLDER``
* Ajout d’un ``Dockerfile`` et publication automatique des images de celui-ci par Github Action

**🐛 Corrections**

* La table ``bdc_statut_cor_text_area`` est correctement peuplée lors de l’intégration de la BDC Statuts.
* Le service systemd ne dépend plus de PostgreSQL pour les cas d’utilisation d’une base de données distante (mais continue de démarrer avant dans le cas d’une base de données locale).

**⚠️ Notes de version**

* Si vous mettez à jour TaxHub, peuplez les données de la table ``bdc_statut_cor_text_area`` en utilisant la commande suivante : 

  ::

    cd ~/taxhub
    source venv/bin/activate
    flask taxref link-bdc-statut-to-areas


1.10.4 (2022-10-24)
-------------------

**🚀 Nouveautés**

* Mise à jour de la documentation d’installation
* Mise à jour des dépendances :

  * RefGeo 1.2.0


1.10.3 (2022-10-20)
-------------------

**🐛 Corrections**

* Correction de la vue matérialisée ``vm_taxref_list_forautocomplete``
* Rendre le stockage des medias sur les services S3 vraiment facultatif
* Installer la BDC statuts version 15 avec Taxref v15


1.10.2 (2022-10-06)
-------------------

**🐛 Corrections**

* Correction du chemin vers les scripts de migration Taxref v15


1.10.1 (2022-09-20)
-------------------

**🐛 Corrections**

* Ajout de ``gunicorn`` au requirements.
* Modification du script de démarrage ``systemd`` pour lancer TaxHub après PostgreSQL.


1.10.0 (2022-03-31)
-------------------

⚠️ Si vous utilisez GeoNature, vous devez mettre à jour celui-ci en version 2.10.

**🚀 Nouveautés**

* Passage à la version 15 de Taxref ainsi que de la BDC statuts, utilisée par défaut pour les nouvelles installations (#322)
* Mise en place de scripts python pour la mise à jour de Taxref à partir de sa version 15, dans le dossier ``apptax/taxonomie/commands/migrate_to_v15``, à la place des scripts shell (#322)
* Ajout de l'option ``--keep-cdnom`` aux scripts de mise à jour de Taxref, pour empêcher la suppression des cd_noms manquants (#306)
* Ajout du champs ``group3_inpn``, ajouté dans la v15 de Taxref
* Ajout des API pour les statuts de protection et de listes rouges (#291)
* Ajout d'une table d'association entre les statuts et le référentiel géographique ``taxonomie.bdc_statut_cor_text_area``. L'association entre les textes et les statuts est réalisée lorsque le texte est associé à une région ou un département (#323)
* Possibilité de passer des paramètres de configuration par variable d’environnement préfixée par ``TAXHUB_``
* Fichiers de log :

  * Les logs sont à présent écrits dans le fichier ``/var/log/taxhub/taxhub.log``
  * L’outil ``logrotate`` est configuré pour assurer la rotation du fichier
  * L’ancien fichier de log ``/var/log/taxhub.log`` est intouché; vous pouvez le supprimer, ou l’archiver manuellement.

* Mise à jour des dépendances :

  * Utils-Flask-SQLAlchemy 0.3.0
  * UsersHub-authentification-module 1.6.0
  * RefGeo 1.1.1

**🐛 Corrections**

* Correction d’un problème lié au double-chargement de Flask en mode développement.
* Correction d’un problème au démarrage de Flask lorsque la base de données n’a pas encore été créée.

**💻 Développement**

* Exécution automatique des tests backend avec Github actions
* Le code est désormais formaté avec Black; une Github action y veille
* Mise à jour de Flask version 1 à 2
* Migrations Alembic : possibilité de rendre l'intégration de la BDC statuts optionnelle
* Ajout de la dépendance au module RefGeo
* Suppression des exemples de taxons (``taxonomie_taxons_example.sql`` et ``taxonomie_attributes_example.sql``)
* Création de commandes pour l'insertion des données du référentiel, hors Alembic (#333)

**⚠️ Notes de version**

* Les branches Alembic ``taxonomie_inpn_data``, ``taxonomie_taxons_example`` et ``taxonomie_attributes_example`` ont été supprimées. Après avoir mis à jour TaxHub en version 1.10, vous devez supprimer toutes références à ces dernières, sans quoi Alembic vous indiquera qu’il ne connait pas certains numéros de révision :

  ::

    (venv)$ flask db exec "delete from public.alembic_version where version_num in ('f61f95136ec3', 'aa7533601e41', '8222017dc3f6')"

* **Si vous n’utilisez pas GeoNature**, vous devez appliquer les évolutions du schéma ``taxonomie`` depuis TaxHub :

  * Se placer dans le dossier de TaxHub : ``cd ~/taxhub``
  * Sourcer le virtualenv de TaxHub : ``source venv/bin/activate``
  * Appliquer les révisions du schéma de la base de données : ``flask db autoupgrade``

* Sinon le faire depuis GeoNature ``(venv)$ geonature db autoupgrade``, après la mise à jour de ce dernier en version 2.10

* La mise à jour de la version 14 à 15 de Taxref est désormais réalisée par des scripts python, disponibles dans le dossier ``apptax/taxonomie/commands/migrate_to_v15``

* Les mises à jour précédentes de Taxref jusqu'à la version 14 restent disponibles dans le dossier ``data/scripts/update_taxref``

* Il est possible d'installer TaxHub avec Taxref v14. Pour cela il faut utiliser les commandes suivantes :

  ::

    flask db upgrade taxonomie@head
    flask taxref import-v14 --skip-bdc-statuts
    flask db upgrade taxhub-admin@head


1.9.4 (2022-01-25)
------------------

**🐛 Corrections**

* Ordonnancement de la route ``/allnamebylist`` par identifiant quand aucun ``search_name`` ne lui est passé en paramètre (pour ordonner les résultats paginés utilisés par Occtax-mobile)

**💻 Développement**

* Utilisation du paramètre ``page`` de Flask à la place du paramètre maison ``offset`` pour la pagination des routes
* Possibilité d'utiliser le fichier ``config.py`` dans les variables d'environnement
* Ajout du fichier de configuration ``apptax/test_config.py`` pour les tests automatisés
* Changement du code http 500 en 400 quand l'``id_liste`` de la route ``/allnamebylist`` n'est pas trouvé

1.9.3 (2022-01-12)
------------------

**🐛 Corrections**

* Correction de la variable ``SCRIPT_NAME`` (#295)

1.9.2 (2021-12-21)
------------------

**🚀 Nouveautés**

* Ajout des champs ``licence`` et ``source`` dans le formulaire d'édition (#151)
* Amélioration de quelques routes

**🐛 Corrections**

* Correction du chemin des médias qui empêchait la récupération des vignettes
* Correction de la génération de la documentation sur Readthedocs
* Correction de la variable ``SCRIPT_NAME`` (#295)
* Suppression de la documentation de l'API qui était cassée

**⚠️ Notes de version**

Si vous mettez à jour TaxHub :

* Vous devez modifier le fichier de configuration ``apptax/config.py`` :

  - Supprimer les lignes suivantes :

  ::

     # File
     import os # A SUPPRIMER
     BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # A SUPPRIMER

  - Si vous l'aviez renseignée dans votre configuration, modifier le paramètre ``UPLOAD_FOLDER = 'static/medias'`` en ``UPLOAD_FOLDER = 'medias'``

1.9.1 (2021-10-19)
------------------

**🐛 Corrections**

* Correction d’un bug qui empêchait l’ajout d’une liste

1.9.0 (2021-10-01)
------------------

**🚀 Nouveautés**

* Packaging de l’application TaxHub
* Passage de ``supervisor`` à ``systemd``

  * Les logs de l’application se trouvent désormais dans le répertoire système ``/var/log/taxhub.log``

* Ajout d’un template de configuration Apache et révision de la documentation sur le sujet
* Gestion de la base de données et de ses évolutions avec `Alembic <https://alembic.sqlalchemy.org/>`_
* Possibilité d’installer le schéma ``taxonomie`` avec Alembic sans passer par une application Flask telle que TaxHub
* Ajout de fonctions permettant la recherche du cd_nom ou cd_ref à partir d'un nom latin (``match_binomial_taxref``), et permettant de vérifier si une valeur est bien un cd_ref existant (``check_is_cd_ref``) (par @DonovanMaillard)
* Ajout d'une fonction ``find_all_taxons_parents(cd_nom)`` retournant les cd_nom de tous les taxons parents d'un cd_nom (par @DonovanMaillard)
* Ajout de la vue ``v_bdc_status`` (par @jpm-cbna)
* Suppression de ``ID_APP`` du fichier de configuration (auto-détection depuis la base de données)
* Mise à jour de `UsersHub-authentification-module <https://github.com/PnX-SI/UsersHub-authentification-module/releases>`__ en version 1.5.3
* Mise à jour de `Utils-Flask-SQLAlchemy <https://github.com/PnX-SI/Utils-Flask-SQLAlchemy/releases>`__ en version 0.2.4

**🐛 Corrections**

* Corrections pour servir TaxHub sur un préfixe (typiquement ``/taxhub``)
* Correction des scripts pour mettre à jour TAXREF (#274 et #283)
* Correction de la valeur par défaut du champs ``taxonomie.bib_listes.id_liste`` (#275)

**⚠️ Notes de version**

* Avec le passage à Alembic pour la gestion de la BDD, les fichiers SQL de création du schéma ``taxonomie`` ont été déplacés dans ``apptax/migrations/data/`` et ils ne sont plus mis à jour à chaque nouvelle version, car ils sont désormais gérés par des migrations Alembic.

Pour mettre à jour TaxHub :

* Suppression de ``supervisor`` :

  * Vérifier que TaxHub n’est pas lancé par supervisor : ``sudo supervisorctl stop taxhub``
  * Supprimer le fichier de configuration de supervisor ``sudo rm /etc/supervisor/conf.d/taxhub-service.conf``
  * Si supervisor n’est plus utilisé par aucun service (répertoire ``/etc/supervisor/conf.d/`` vide), il peut être désinstallé : ``sudo apt remove supervisor``

* Installer le paquet ``python3-venv`` nouvellement nécessaire : ``sudo apt install python3-venv``
* Déplacer le fichier de configuration ``config.py`` situé à la racine de TaxHub dans le sous-dossier ``apptax``
* Suivre la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application
* Si vous servez TaxHub sur un préfixe (*e.g.* ``/taxhub``), rajouter dans ``config.py`` le paramètre suivant : ``APPLICATION_ROOT = '/taxhub'``

* Passage à ``systemd`` :

  * Le fichier ``/etc/systemd/system/taxhub.service`` doit avoir été installé par le script ``install_app.sh``
  * Pour démarrer TaxHub : ``sudo systemctl start taxhub``
  * Pour activer le lancement automatiquement de TaxHub au démarrage : ``sudo systemctl enable taxhub``

* Révision de la configuration Apache :

  * Le script d’installation ``install_app.sh`` aura installé le fichier ``/etc/apache2/conf-available/taxhub.conf`` permettant de servir TaxHub sur le préfixe ``/taxhub``.
  * Vous pouvez utiliser ce fichier de configuration soit en l’activant (``sudo a2enconf taxhub``), soit en l’incluant dans la configuration de votre vhost (``Include /etc/apache2/conf-available/taxhub.conf``).
  * Si vous gardez votre propre fichier de configuration et que vous servez TaxHub sur un préfixe (typiquement ``/taxhub``), assurez vous que ce préfixe figure bien également à la fin des directives ``ProxyPass`` et ``ProxyPassReverse`` comme c’est le cas dans le fichier ``/etc/apache2/conf-available/taxhub.conf``.
  * Si vous décidez d’utiliser le fichier fourni, pensez à supprimer votre ancienne configuration apache (``sudo a2dissite taxhub && sudo rm /etc/apache2/sites-available/taxhub.conf``).

* **Si vous n’utilisez pas GeoNature**, vous devez appliquer les évolutions du schéma ``taxonomie`` depuis TaxHub :

  * Se placer dans le dossier de TaxHub : ``cd ~/taxhub``
  * Sourcer le virtualenv de TaxHub : ``source venv/bin/activate``
  * Indiquer à Alembic que vous possédez déjà la version 1.8.1 du schéma ``taxonomie`` et les données d’exemples : ``flask db stamp 3fe8c07741be``
  * Indiquer à Alembic que vous possédez les données INPN en base : ``flask db stamp f61f95136ec3``
  * Appliquer les révisions du schéma ``taxonomie`` : ``flask db upgrade taxonomie@head``

1.8.1 (2021-07-01)
------------------

**🐛 Corrections**

* Correction de la migration Taxref v11 vers v13 pour les versions de PostgreSQL < 12

**⚠️ Notes de version**

* Vous pouvez passer directement à cette version, mais en suivant les notes des versions intermédiaires

1.8.0 (2021-06-22)
------------------

**🚀 Nouveautés**

* Passage à la version 14 de Taxref, utilisée par défaut pour les nouvelles installations
* Intégration du référentiel BDC statuts (https://inpn.mnhn.fr/telechargement/referentielEspece/bdc-statuts-especes), peuplé lors du passage à Taxref v14. Pour des raisons de compatibilité avec GeoNature les anciens statuts de protection et les listes rouges sont toujours présents (#157)
* Support du stockage des medias sur les services de stockages S3 (#248 par @jbdesbas)
* Ajout d'un champs ``code_liste`` dans la table ``taxonomie.bib_listes`` pour utiliser des codes plutôt que des identifiants et faciliter l'interopérabilité des données entre outils
* Ajout d'un paramètre ``fields`` à la route ``/taxref/search/`` afin de pouvoir récupérer dans la réponse des champs supplémentaires selon les besoins (#243)
* Recherche non sensible aux accents pour la route ``allnamebylist``
* Mise à jour de AngularJS en version 1.8.0
* Mise à jour de différentes dépendances Python

**🐛 Corrections**

* Correction de la génération des vignettes des images

**⚠️ Notes de version**

* Exécuter la commande suivante pour ajouter l'extension PostgreSQL ``unaccent``, en remplaçant la variable ``$db_name`` par le nom de votre BDD : ``sudo -n -u postgres -s psql -d $db_name -c 'CREATE EXTENSION IF NOT EXISTS "unaccent";'``
* Exécutez le script SQL de mise à jour de la BDD (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.7.3to1.8.0.sql)
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application
* Vous pouvez exécuter la mise à jour vers Taxref v14, en suivant la procédure et les scripts dédiés (https://github.com/PnX-SI/TaxHub/tree/master/data/scripts/update_taxref). Cela peuplera aussi la BDC statuts.
* Pour des raisons de compatibilité avec GeoNature, laissez les ``code_liste`` au format numérique pour le moment

1.7.3 (2020-09-29)
------------------

**🚀 Nouveautés**

* Ajout de tests unitaires
* Mise à jour des dépendances (``psycopg2`` et ``SQLAlchemy``)

**🐛 Corrections**

* Correction d'un bug sur la récupération des attributs des taxons (#235 par @jbdesbas)
* Script de récupération des médias sur INPN. Le script continue lorsqu'un appel à l'API renvoie un autre code que 200

1.7.2 (2020-07-03)
------------------

**🚀 Nouveautés**

* Ajout du nom vernaculaire (``nom_vern``) dans la vue matérialisée ``taxonomie.vm_taxref_list_forautocomplete`` et dans la route associée (``api/taxref/allnamebylist/``)

**🐛 Corrections**

* Correction de la pagination des routes quand le paramètre ``offset`` est égal à zéro (nécessaire pour Sync-mobile)

**⚠️ Notes de version**

* Exécutez le script SQL de mise à jour de la BDD (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.7.1to1.7.2.sql)
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.7.1 (2020-07-02)
------------------

**🐛 Corrections**

* Correction et homogénéisation des paramètres ``offset`` et ``page`` sur toutes les routes (#229)
* Correction de la route de récupération de la configuration sans le "/" (#228)
* Suppression des doublons de la route ``allnamebylist``, entrainant un nombre de résultats différent du paramètre ``limit`` fourni

1.7.0 (2020-06-17)
------------------

**🚀 Nouveautés**

* Mise à jour de Taxref en version 13
* Intégration brute de la Base de connaissance des statuts des espèces correspondant à la version 13 de Taxref, en vue de la révision des statuts de protection (#157)
* Migration de la librairie OpenCV vers PIL (plus légère) pour le redimensionnement des images et suppression de la librairie dépendante  NumPy (#209)
* Mise à jour des librairies Python (Flask 1.1.1, Jinja 2.11.1, Werkzeug 1.0.0, gunicorn20.0.4) et Javascript (AngularJS 1.7.9, Bootstrap 3.4.1)
* Suppression du paramètre ``id_application`` du fichier ``static/app/constants.js`` de façon à ce qu'il soit récupéré de façon dynamique
* Ajout de fonctions génériques de détection, suppression et création des vues dépendantes dans le schéma ``public`` (``data/generic_drop_and_restore_deps_views.sql``)
* Route ``allnamebylist`` enrichie avec un paramètre ``offset`` pour que l'application Occtax-mobile puisse récupérer les taxons par lots (#208)
* Utilisation du ``cd_sup`` au lieu du ``cd_taxsup`` dans la fonction ``taxonomie.find_all_taxons_children()`` pour prendre en compte les rangs intermediaires
* Ajout de la colonne famille au modèle ``VMTaxrefHierarchie`` (#211)
* Ajout d'un manuel administrateur listant les fonctions SQL de la BDD (par @jbdesbas)
* Révision et compléments de la documentation (par @ksamuel)
* Ajout d'un lien vers le manuel utilisateur depuis la barre de navigation de l'application
* Changement de modélisation de la table ``vm_taxref_list_forautocomplete`` qui redevient une vue matérialisée (#219). A rafraichir quand on met à jour Taxref

**🐛 Corrections**

* Correction d'un bug de suppression des attributs suite à une erreur d'enregistrement (#80)
* Correction d'un bug lors de la modification d'un média
* Correction des doublons (#216) et des noms manquants (#194) dans la vue matérialisée ``vm_taxref_list_forautocomplete`` (#219)
* Impossibilité d'associer une valeur nulle à un attribut
* Nettoyage et suppression des scripts SQL et de leurs mentions à GeoNature v1 et UsersHub v1

**⚠️ Notes de version**

* Vous pouvez supprimer le paramètre ``id_application`` du fichier ``static/app/constant.js`` car il n'est plus utilisé
* Vous pouvez supprimer les anciennes listes de taxons qui correspondaient à des groupes utilisés par GeoNature v1 (Flore, Fonge, Vertébrés, Invertébrés, Amphibiens, Oiseaux, Poissons...)
* Exécutez le script SQL de mise à jour de la BDD (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.6.5to1.7.0.sql)
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application
* Vous pouvez mettre à jour Taxref en version 13 avec la documentation et les scripts du dossier ``data/scripts/update_taxref/`` (https://github.com/PnX-SI/TaxHub/tree/master/data/scripts/update_taxref)

1.6.5 (2020-02-17)
------------------

**Corrections**

* Compatibilité Python > 3.5 : utilisation de ``<ImmutableDict>.to_dict()`` pour convertir le résultat d'un formulaire en dictionnaire (Corrige le bug d'ajout de média)

**Notes de version**

* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.6.4 (2020-02-13)
------------------

**Corrections**

* Logging des erreurs lorsque des exceptions sont attrapées (évite les erreurs silencieuses)
* Gestion des taxons synonymes dans la vue gérant la recherche des taxons (``vm_taxref_list_forautocomplete``)
* Modification de la méthode d'installation du virtualenv
* Utilisation de nvm pour installer node et npm (uniformisation avec GeoNature)

**Notes de version**

* Exécuter le script de migration SQL (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.6.3to1.6.4.sql)
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

1.6.3 (2019-07-16)
------------------

**Nouveautés**

* Intégration du trigramme dans le champs de recherche de taxon de TaxHub
* Route de recherche de taxon : Possibilité de limiter à un rang
* Ajout de la fonction ``taxonomie.find_all_taxons_children`` qui renvoie tous les taxons enfants d'un taxon à partir d'un ``cd_nom``
* Mise à jour de OpenCV en 3.4.2

**Corrections**

* Suppression de l'index ``taxref.i_taxref_cd_nom`` inutile (#192)

**Notes de version**

* Exécuter le script de migration SQL (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.6.2to1.6.3.sql)
* Suivez la procédure standard de mise à jour de TaxHub : https://taxhub.readthedocs.io/fr/latest/installation.html#mise-a-jour-de-l-application

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
* Pour ne pas avoir de conflits de sessions d'authentification entre TaxHub et GeoNature, ajouter une variable ``ID_APP`` dans le fichier de configuration ``config.py`` et y mettre l'identifiant de l'application TaxHub tel qu'il est inscrit dans la table ``utilisateurs.t_applications``. Exemple : ``ID_APP = 2``
* Exécuter le script de migration SQL : https://github.com/PnX-SI/TaxHub/blob/master/data/update1.6.1to1.6.2.sql
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
* Exécutez le script de mise de la BDD : https://github.com/PnX-SI/TaxHub/blob/master/data/update1.5.1to1.6.0.sql
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
* Exécutez le script de mise à jour de la BDD TaxHub (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.5.0to1.5.1.sql)

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
- Exécutez le script SQL de mise à jour de la BDD (https://github.com/PnX-SI/TaxHub/blob/master/data/update1.3.2to1.4.0.sql)
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

  - Exécuter la commande suivante depuis la racine du projet TaxHub ``unzip data/inpn/LR_FRANCE.zip -d /tmp``
  - Exécuter le fichier ``data/update1.1.0to1.1.1.sql``

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

Première version fonctionnelle et déployable de TaxHub (Python Flask)

**Fonctionnalités**

- Visualisation de Taxref
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
