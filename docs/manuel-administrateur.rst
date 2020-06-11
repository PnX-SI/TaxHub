MANUEL ADMINISTRATEUR
=====================

Fonctions SQL
-------------
La base de données comprend plusieurs fonctions permettant d'utiliser plus aisément le référentiel Taxref.

Arbre taxonomique
^^^^^^^^^^^^^^^^^

``find_cdref(cd_nom int) --> int``
  cd_ref d'un taxon

``find_cdref_sp(cd_nom int) --> int``
  cd_nom de l'espèce de référence s'il s'agit d'une espèce ou d'un taxon infra-spécifique. Retourn ``NULL`` s'il s'agit d'un taxon supra-spécifique.

``find_all_taxons_children(cd_nom int) --> int[]``
  Les cd_nom des taxons inférieurs au taxon en entrée.

``find_all_taxons_children(cd_nom int[]) --> table``
  Les cd_nom des taxons inférieurs aux taxons en entrée.

``find_all_taxons_parents(cd_nom int) --> int[]``
  Les cd_nom des taxons supérieurs au taxon en entrée, du plus bas vers le plus haut (domaine).

``find_all_taxons_parents_t(cd_nom int) --> table``
  Les cd_nom des taxons supérieurs au taxon en entrée, du plus bas vers le plus haut (domaine). Sous forme de table avec le rang indiqué.

``find_lowest_common_ancestor(cd_nom1 int, cd_nom2 int) --> int``
  cd_ref de l'ancêtre commun le plus récent à deux taxons.

``find_regne(cd_nom int) --> text``
  Libellé du règne du taxon.
