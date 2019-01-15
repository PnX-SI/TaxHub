-- Ajout d'un index sur la table vm_taxref_list_forautocomplete pour améliorer les performances
CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name 
  ON taxonomie.vm_taxref_list_forautocomplete USING GIST (search_name gist_trgm_ops);
