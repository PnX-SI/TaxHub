MANUEL ADMINISTRATEUR
=====================

Commandes
---------

- ``flask taxref info`` : Indique le nombre de taxon et de status  contenu dans la base

- ``flask taxref link-bdc-statut-to-areas`` : Permet d'associer les statuts aux départements contenus dans le ref_geo

- ``flask taxref enable-bdc-statut-text -d <MON_DEP_1> -d <MON_DEP_2> --clean`` : Permet d'activer les statuts par départements. Il est possible de spécifier plusieurs départements (par ``code_area``).

Mise à jour de Taxref
---------------------

Un ensemble de commandes permettent de réaliser un changement de version de Taxref.

La documentation détaillée est accessible ici : https://github.com/PnX-SI/TaxHub/tree/master/apptax/taxonomie/commands/migrate_taxref


Gestion des permissions
-----------------------

.. warning::
    Si vous avez installé TaxHub via GeoNature, les permissions ne sont pas gérées de la mêmesmanière et sont uniquement piloté par le module de gestion des permissions de GeoNature (voir la documentation de GeoNature à ce sujet)

La gestion des permissions de l'application TaxHub se fait via les "profils" UsersHub.

- Profil 6 = peut administrer tous les tables : création / modification / suppression de liste, d'attributs, et de thêmes
- Profils 2 : peut ajouter / modifier des médias et attributs sur les taxons. Peut ajouter / enlever des taxons dans de listes


Fonctions SQL
-------------

La base de données comprend plusieurs fonctions permettant d'utiliser plus aisément le référentiel Taxref.

Arbre taxonomique
^^^^^^^^^^^^^^^^^

- ``find_cdref(cd_nom int) --> int`` : cd_ref d'un taxon

- ``find_cdref_sp(cd_nom int) --> int`` : cd_nom de l'espèce de référence s'il s'agit d'une espèce ou d'un taxon infra-spécifique. Retourn ``NULL`` s'il s'agit d'un taxon supra-spécifique.

- ``find_all_taxons_children(cd_nom int) --> int[]`` : Les cd_nom des taxons inférieurs au taxon en entrée.

- ``find_all_taxons_children(cd_nom int[]) --> table`` : Les cd_nom des taxons inférieurs aux taxons en entrée.

- ``find_all_taxons_parents(cd_nom int) --> int[]`` : Les cd_nom des taxons supérieurs au taxon en entrée, du plus bas vers le plus haut (domaine).

- ``find_all_taxons_parents_t(cd_nom int) --> table`` : Les cd_nom des taxons supérieurs au taxon en entrée, du plus bas vers le plus haut (domaine). Sous forme de table avec le rang indiqué.

- ``find_lowest_common_ancestor(cd_nom1 int, cd_nom2 int) --> int`` : cd_ref de l'ancêtre commun le plus récent à deux taxons.

- ``find_regne(cd_nom int) --> text`` : Libellé du règne du taxon.

- ``check_is_cd_ref(mycdnom integer) --> boolean`` : True si l'argument donné est un cd_ref existant

- ``match_binomial_taxref(mytaxonname character varying)`` : Cd_nom ou Cd_ref correspondant au nom latin donné en argument (si un seul cd possible, sinon NULL)
