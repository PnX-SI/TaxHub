Update Taxref
==============

Script de migration permettant de passer d'une version de Taxref à l'autre

Le passage vers une nouvelle version de Taxref se fait en 3 étapes, disponibles sous forme de scripts ``.sh`` dans le répertoire  ``data/scripts/update_taxref/`` :

**1. import_taxref_data_vXXX.sh** : import de Taxref et détection des changements de ``bib_noms``.

Un export des changements est réalisé à l'issue du script.

* Télécharge la version de taxref et import dans taxonomie.import_taxref
* Correction des bib_noms ayant disparus
* Détection et export des changements à venir

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
