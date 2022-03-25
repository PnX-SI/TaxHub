DROP  TABLE IF EXISTS taxonomie.tmp_bib_noms_copy;

CREATE TABLE taxonomie.tmp_bib_noms_copy (
    id_nom serial PRIMARY KEY,
    cd_nom integer,
    cd_ref integer,
    nom_francais character varying(1000),
    comments character varying(1000),
    commentaire_disparition Varchar(500),
    cd_nom_remplacement int,
    deleted boolean DEFAULT(FALSE),
    tmp_import boolean
);

INSERT INTO taxonomie.tmp_bib_noms_copy (
    id_nom, cd_nom, cd_ref, nom_francais, comments
)
SELECT id_nom, cd_nom, cd_ref, nom_francais, comments
FROM taxonomie.bib_noms;


SELECT setval(
    'taxonomie.tmp_bib_noms_copy_id_nom_seq',
    (SELECT max(id_nom) FROM  taxonomie.tmp_bib_noms_copy ),
    true
);

--- CAS 1 - cd_nom de remplacement à utiliser.
UPDATE taxonomie.tmp_bib_noms_copy n  SET deleted = true ,
	commentaire_disparition = raison_suppression ||  COALESCE(' nouveau cd_nom :' || a.cd_nom_remplacement, ''),
	cd_nom_remplacement =  a.cd_nom_remplacement
FROM (
	SELECT d.*
	FROM taxonomie.bib_noms n
	JOIN taxonomie.cdnom_disparu d
	ON n.cd_nom = d.cd_nom
) a
WHERE n.cd_nom = a.cd_nom;

------------- Cas avec cd_nom de remplacement
-- Ajout du cd_nom de remplacement quand il n'existait pas dans bib_noms
INSERT INTO taxonomie.tmp_bib_noms_copy(cd_nom, cd_ref, nom_francais, tmp_import)
SELECT d.cd_nom_remplacement, n.cd_ref, n.nom_francais, true
FROM taxonomie.tmp_bib_noms_copy n
JOIN taxonomie.cdnom_disparu d ON n.cd_nom = d.cd_nom
WHERE NOT n.cd_nom_remplacement IS NULL
ON CONFLICT DO NOTHING;
