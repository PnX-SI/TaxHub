Update Taxref
==============

Script de migration permettant de mettre à jour une version de Taxref à une autre.

Avant de commencer : 

* La migration d'une version de Taxref est une opération conséquente. Ce script permet d'automatiser au maximum les opérations, mais certaines parties reviennent à l'administrateur de données et il est important de comprendre les différentes étapes.
* Il est important aussi de faire une sauvegarde avant de réaliser ces opérations et de faire des tests et vérifications des données au fur et à mesure et à la fin des opérations.
* Une partie des scripts est réalisée avec l'utilisateur propriétaire de la BDD défini dans le fichier ``settings.ini``. Une autre est réalisée avec le super-utilisateur ``postgres`` pour pouvoir réaliser les taches de copie notamment. Ainsi les scripts ne fonctionnent que si la BDD est sur le même serveur que celui où sont exécutés les scripts (``$db_host = localhost``).

Le passage vers une nouvelle version de Taxref se fait en 3 étapes, disponibles sous forme de scripts ``.sh`` dans le répertoire  ``data/scripts/update_taxref/`` :

**1. import_taxref_data_vXXX.sh** : import de Taxref et détection des changements de ``bib_noms``.

Un export des changements est réalisé à l'issue du script, dans le fichier ``/tmp/nb_changements.csv``.

* Télécharge la version de Taxref et import dans la table ``taxonomie.import_taxref`` (+ ``taxonomie.cdnom_disparu`` et ``taxonomie.taxref_changes``)
* Analyse des données dans la Synthèse de GeoNature et identification de celles dont le cd_nom a disparu dans la nouvelle version de Taxref (listés dans le fichier ``/tmp/liste_cd_nom_disparus_synthese.csv``)
* Remplacement des ``cd_nom`` ayant disparus dans la table ``taxonomie.bib_noms`` et répercussions dans ``taxonomie.cor_nom_liste``
* Liste des cd_nom supprimés de ``taxonomie.bib_noms`` dans le fichier ``/tmp/liste_cd_nom_disparus_bib_noms.csv``
* Détection et export des changements à venir dans le schéma temporaire ``tmp_taxref_changes`` et sa table ``comp_grap``
* Liste dans le fichier ``/tmp/nb_changements.csv`` les changements qui vont être réalisés et les potentiels conflits qu'ils faut résoudre en amont

**2. apply_changes.sh 13** : Application des modifications dues au changement de taxref. Le script ne peut se lancer que s'il n'y a plus de conflits.

Il est possible d'automatiser la résolution de conflit un créant les scripts suivants à partir des exemples (``.sample``) :

* ``2.1_taxref_changes_corrections_pre_detections.sql``
* ``2.2_taxref_changes_corrections_post_detections.sql`` (permet notament de changer la colonne action et d'indiquer si on veut dupliquer les médias et attributs)

Ce script met également à jour les statuts taxonomiques. Il est possible de créer un script ``4.2_stpr_update_concerne_mon_territoire.sql`` (à partir de l'exemple ``.sample``) pour réaliser la selection des statuts concernant la structure.

**3. clean_db.sh** : Suppression des tables résiduelles

Les logs de ces scripts sont disponibles dans le répertoire ``montaxhub/var/log/updatetaxrefv11``.

.. image:: images/update-taxref-cas-1.jpg

.. image:: images/update-taxref-cas-2.jpg

.. image:: images/update-taxref-cas-3.jpg

.. image:: images/update-taxref-cas-4.jpg
