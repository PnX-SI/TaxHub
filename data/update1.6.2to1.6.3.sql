--OBJECTIF : supprimer id_nom et le replacer par cd_nom

--suppression des contraintes sur id_nom
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_noms_fkey;
--suppression de la FK de bib_noms
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT bib_noms_pkey;

--modification de la FK de bib_noms vers cd_nom
ALTER TABLE taxonomie.bib_noms ADD CONSTRAINT bib_noms_pkey PRIMARY KEY(cd_nom);

--création du champ pour la nouvelle FK cd_nom dans cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste ADD COLUMN cd_nom integer;

--convertir les id_nom en cd_nom dans cor_nom_liste
UPDATE taxonomie.cor_nom_liste
SET cd_nom = n.cd_nom
FROM taxonomie.bib_noms n
WHERE n.id_nom = taxonomie.cor_nom_liste.id_nom

--suppression de la séquence inutile sur l'ex PK de bib_noms
ALTER TABLE taxonomie.bib_noms
   ALTER COLUMN id_nom DROP DEFAULT;
ALTER TABLE taxonomie.bib_noms
   ALTER COLUMN id_nom DROP NOT NULL;
DROP SEQUENCE taxonomie.bib_noms_id_nom_seq;

--suppression de la contrainte d'unicité devenue inutile
ALTER TABLE taxonomie.t_medias DROP CONSTRAINT fk_t_media_bib_noms;
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT bib_noms_cd_nom_key;

--création de la FK cd_nom dans cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste
  ADD CONSTRAINT cor_nom_liste_bib_noms_fkey FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.bib_noms (cd_nom) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION;
      
--restauration de la FK sur t_medias
ALTER TABLE taxonomie.t_medias
  ADD CONSTRAINT fk_t_media_bib_noms FOREIGN KEY (cd_ref)
      REFERENCES taxonomie.bib_noms (cd_nom) MATCH FULL
      ON UPDATE CASCADE ON DELETE NO ACTION;

--A voir si on drop tout de suite les id_nom
--ALTER TABLE taxonomie.bib_noms DROP COLUMN id_nom;