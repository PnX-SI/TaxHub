--Création d'index uniques sur les vues matérialisées 
--afin de permettre le refresh
CREATE UNIQUE INDEX i_unique_ordre
  ON taxonomie.vm_ordre
  USING btree
  (ordre);
CREATE UNIQUE INDEX i_unique_phylum
  ON taxonomie.vm_phylum
  USING btree
  (phylum);
CREATE UNIQUE INDEX i_unique_regne
  ON taxonomie.vm_regne
  USING btree
  (regne);
CREATE UNIQUE INDEX i_unique_famille
  ON taxonomie.vm_famille
  USING btree
  (famille);
CREATE UNIQUE INDEX i_unique_classe
  ON taxonomie.vm_classe
  USING btree
  (classe);
CREATE UNIQUE INDEX i_unique_group1_inpn
  ON taxonomie.vm_group1_inpn
  USING btree
  (group1_inpn);
CREATE UNIQUE INDEX i_unique_group2_inpn
  ON taxonomie.vm_group2_inpn
  USING btree
  (group2_inpn);