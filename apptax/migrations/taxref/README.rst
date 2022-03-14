Update Taxref
==============

Scripts de migration permettant de mettre à jour une version de Taxref à une autre.

Avant de commencer :

* La migration d'une version de Taxref est une opération conséquente. Ce script permet d'automatiser au maximum les opérations, mais certaines parties reviennent à l'administrateur de données et il est important de comprendre les différentes étapes.
* Il est important aussi de faire une sauvegarde avant de réaliser ces opérations et de faire des tests et vérifications des données au fur et à mesure et à la fin des opérations.

* Mettre à jour la structure de la base :
    * **Si vous n’utilisez pas GeoNature**, vous devez appliquer les évolutions du schéma ``taxonomie`` depuis TaxHub :

        * Se placer dans le dossier de TaxHub : ``cd ~/taxhub``
        * Sourcer le virtualenv de TaxHub : ``source venv/bin/activate``
        * Appliquer les révisions du schéma ``taxonomie`` : ``flask db upgrade taxonomie@head``

    * Sinon le faire depuis GeoNature ``(venv)$ geonature db autoupgrade``

Le passage vers une nouvelle version de Taxref se fait en 2 étapes, disponibles sous forme de commandes python :
Les commandes sont accésibles via l'application FLASK. Pour les activer il faut :

::

    # Aller dans le répertoire de taxhub
    cd $TAXHUB_PATH
    # Activer le virtual env
    source venv/bin/activate
    # Charger l'application FLASK
    export FLASK_APP=apptax/app.py



**update-taxref-v15** : import de Taxref et détection des changements de ``bib_noms``.

Un export des changements est réalisé à l'issue du script, dans le fichier ``liste_changements.csv``.

* Télécharge la version de Taxref et import dans les tables ``taxonomie.import_taxref``, ``taxonomie.cdnom_disparu``
* Analyse des données dans la Synthèse de GeoNature et identification de celles dont le cd_nom a disparu dans la nouvelle version de Taxref (listés dans le fichier ``liste_cd_nom_disparus_synthese.csv``)
* Insertion des cd_noms de remplacement de ceux ayant disparus dans ``bib_noms``, si non déjà présents
* Identification des cd_noms ayant disparu dans la table ``taxonomie.bib_noms``
* Liste des cd_nom supprimés de ``taxonomie.bib_noms`` dans le fichier ``liste_cd_nom_disparus_bib_noms.csv``
* Détection et export des changements à venir dans le schéma temporaire ``tmp_taxref_changes`` et sa table ``comp_grap``
* Liste dans le fichier ``iste_changements.csv`` les changements qui vont être réalisés (et leur nombre dans le fichier ``nb_changements.csv``) et les potentiels conflits qu'il faut résoudre en amont

Pour exécuter ce script il faut lancer la commande suivante :

::

    flask taxref_migration update-taxref-v15

Analysez les fichiers CSV générés dans le dossier ``tmp``. Réalisez les corrections de données en fonction :

- Répercuter les conséquences des cd_noms disparus sur les données de GeoNature (Synthèse, Occtax et éventuelles autres sources).
- Gérer les attributs en conflit (cd_nom mergés et attributs incohérents)
- Gérer les éventuels splits
- Vérifier les éventuels taxons locaux (Hors Taxref) si ils ont été ajoutés dans la nouvelle version de Taxref

Toutes ces opérations peuvent être regroupés dans un fichier SQL exécuté dans le script d'application des mises à jour.


**test-changes-detection** : Test des changements qui seront réalisés lors de la migration vers taxref v15.

::

    flask taxref_migration test-changes-detection


::

    options
    --keep-cdnom: Indique si l'on souhaite concerver les cd_noms manquants au lieu de les supprimer


**apply-changes** : Application des modifications dues au changement de Taxref.

Le script ne peut s'exécuter entièrement que s'il n'y a plus de conflits. Le script vous indiquera les éventuelles corrections restant à faire. Les différents fichiers CSV du dossier ``tmp`` seront mis à jour par ce script, ainsi qu'un fichier complémentaire ``liste_donnees_cd_nom_manquant.csv``.

Lancer le script avec la commande

::

    flask taxref_migration apply-changes


::


    options
    --keep-oldtaxref: Indique si l'on souhaite concerver l'ancienne version du referentiel taxref
    --keep-oldbdc: Indique si l'on souhaite concerver l'ancienne version du referentiel bdc_status
    --keep-cdnom: Indique si l'on souhaite concerver les cd_noms manquants au lieu de les supprimer
    --script_predetection MON_FICHIER: Emplacement d'un fichier sql de correction avant la detection des changements
    --script_postdetection MON_FICHIER: Emplacement d'un fichier sql de correction après la detection des changements


Il est possible de scripter la résolution de conflits en spécifiant dans les paramètres script_predetection script_postdetection. Des exemples sont disopnibles (``.sample``) :

* ``2.1_taxref_changes_corrections_pre_detections.sql.sample`` (pour les corrections des données d'observation ainsi que les éventuelles désactivations de contraintes vers le champs ``taxonomie.taxref.cd_nom``)
* ``2.2_taxref_changes_corrections_post_detections.sql.sample`` (utile surtout dans le cas de splits, permet notamment de changer la colonne ``action`` de la table ``tmp_taxref_changes.comp_grap`` et d'indiquer si on veut dupliquer les médias et attributs)


Après correction des données d'observation (Occtax, Synthèse...), vous pourrez relancer le script.

* Le script liste dans la table ``tmp_taxref_changes.dps_fk_cd_nom`` toutes les tables de la BDD contenant des cd_noms ayant disparus, ainsi que les cd_nom concernés (en s'appuyant sur les clés étrangères connectées au champs ``taxref.cd_nom``). Le résultat est exporté dans le fichier ``liste_donnees_cd_nom_manquant.csv``
* Mise à jour du contenu de la table ``taxonomie.taxref`` à partir de la table ``taxonomie.import_taxref`` (update champs, ajout nouveaux noms et suppression des noms disparus)
* Répercussion dans la table ``taxonomie.cor_nom_liste`` des cd_noms remplacés et supprimés
* Mise à jour des cd_ref de ``taxonomie.bib_noms`` en fonction des cd_noms, suppression des noms disparus, ajout des noms de références manquants
* Répercussion des évolutions de Taxref sur les tables ``taxonomie.t_medias`` et ``taxonomie.cor_taxon_attribut`` en fonction des cas et actions définis dans la table ``tmp_taxref_changes.comp_grap``
* Import de la BDC statuts de l'INPN
* Traitement de la BDC statuts et structuration
*  Suppression des tables résiduelles

.. image:: ../../../data/scripts/update_taxref/images/bdc_statut.png


.. image:: ../../../data/scripts/update_taxref/images/update-taxref-cas-1.jpg

.. image:: ../../../data/scripts/update_taxref/images/update-taxref-cas-2.jpg

.. image:: ../../../data/scripts/update_taxref/images/update-taxref-cas-3.jpg

.. image:: ../../../data/scripts/update_taxref/images/update-taxref-cas-4.jpg
