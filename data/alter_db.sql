DROP MATERIALIZED VIEW taxonomie.vm_taxref_forautocomplete;
CREATE MATERIALIZED VIEW taxonomie.vm_taxref_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  t.id_rang
 FROM ( SELECT t_1.cd_nom,
	  t_1.cd_ref,
          concat(t_1.lb_nom, ' = ', t_1.nom_complet_html) AS search_name,
          t_1.nom_valide,
          t_1.lb_nom,
          t_1.regne,
          t_1.group2_inpn,
          t_1.id_rang
         FROM taxonomie.taxref t_1
      UNION
       SELECT t_1.cd_nom,
	  t_1.cd_ref,
          concat(n.nom_francais, ' = ', t_1.nom_complet_html) AS search_name,
          t_1.nom_valide,
          t_1.lb_nom,
          t_1.regne,
          t_1.group2_inpn,
          t_1.id_rang
         FROM taxonomie.taxref t_1
         JOIN taxonomie.bib_noms n
         ON t_1.cd_nom = n.cd_nom
        WHERE t_1.nom_vern IS NOT NULL
   ) t
