MANUEL ADMINISTRATEUR
=====================


Fonctions SQL
-------------

Arbre taxonomique
^^^^^^^^^^^^^^^^^

``find_cdref(cd_nom int) --> int``

``find_cdref_sp(cd_nom int) --> int``

``find_all_taxons_children(cd_nom int) -->int``

``find_all_taxons_children(cd_nom int[]) --> table``

``find_all_taxons_parents(cd_nom int) --> int[]``

``find_all_taxons_parents_t(cd_nom int) --> table``

``find_lowest_common_ancestor(cd_nom int) --> int``

``find_regne(cd_nom int) --> text``


