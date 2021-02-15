--Rajouter une version sans accent du nom dans vm_taxref_list_for_autocomplete

CREATE EXTENSION IF NOT EXISTS UNACCENT;

DROP MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete;

CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
TABLESPACE pg_default
AS SELECT row_number() OVER () AS gid,
    t.cd_nom,
    t.cd_ref,
    t.search_name,
    t.nom_valide,
    t.lb_nom,
    t.nom_vern,
    t.regne,
    t.group2_inpn
   FROM ( SELECT t_1.cd_nom,
            t_1.cd_ref,
            concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
            t_1.nom_valide,
            t_1.lb_nom,
            t_1.nom_vern,
            t_1.regne,
            t_1.group2_inpn
           FROM taxonomie.taxref t_1
        UNION
         SELECT DISTINCT t_1.cd_nom,
            t_1.cd_ref,
            concat(split_part(t_1.nom_vern::text, ','::text, 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
            t_1.nom_valide,
            t_1.lb_nom,
            t_1.nom_vern,
            t_1.regne,
            t_1.group2_inpn
           FROM taxonomie.taxref t_1
          WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref
        UNION
        SELECT DISTINCT t_1.cd_nom,
                    t_1.cd_ref,
                    unaccent(concat(split_part(t_1.nom_vern::text, ','::text, 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']')) AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                   FROM taxonomie.taxref t_1
                  WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref ) t
WITH DATA;

-- View indexes:
CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom ON taxonomie.vm_taxref_list_forautocomplete USING btree (cd_nom);
CREATE UNIQUE INDEX i_vm_taxref_list_forautocomplete_gid ON taxonomie.vm_taxref_list_forautocomplete USING btree (gid);
CREATE INDEX i_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete USING gin (search_name gin_trgm_ops);


COMMENT ON MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete IS 'Vue matérialisée permettant de faire des autocomplete construite à partir d''une requete sur tout taxref.
Pour index, cf https://niallburkley.com/blog/index-columns-for-like-in-postgres/';


