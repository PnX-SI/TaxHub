-- ----------------------------------------------------------------------
-- Create a copy of bib_noms table
DROP TABLE IF EXISTS taxonomie.tmp_bib_noms_copy ;

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

INSERT INTO taxonomie.tmp_bib_noms_copy (id_nom, cd_nom, cd_ref, nom_francais, comments)
    SELECT id_nom, cd_nom, cd_ref, nom_francais, comments
    FROM taxonomie.bib_noms ;

SELECT setval(
    'taxonomie.tmp_bib_noms_copy_id_nom_seq',
    (SELECT max(id_nom) FROM  taxonomie.tmp_bib_noms_copy ),
    true
);


-- ----------------------------------------------------------------------
-- CASE 1 - Deleted cd_nom with replacement

-- Update tmp_bib_noms_copy fields about deleted cd_nom
UPDATE taxonomie.tmp_bib_noms_copy AS nc SET
    deleted = true,
    commentaire_disparition = (
        a.raison_suppression || COALESCE(' nouveau cd_nom :' || a.cd_nom_remplacement, '')
    ),
    cd_nom_remplacement = a.cd_nom_remplacement
FROM (
    SELECT d.*
    FROM taxonomie.bib_noms AS n
        JOIN taxonomie.cdnom_disparu AS d
            ON n.cd_nom = d.cd_nom
) AS a
WHERE nc.cd_nom = a.cd_nom ;

-- Add replacement cd_nom when not already exists in tmp_bib_noms_copy
-- TODO: check if this query is mandatory and not a duplicate of previous queries !
INSERT INTO taxonomie.tmp_bib_noms_copy (cd_nom, cd_ref, nom_francais, tmp_import)
    SELECT d.cd_nom_remplacement, nc.cd_ref, nc.nom_francais, true
    FROM taxonomie.tmp_bib_noms_copy AS nc
        JOIN taxonomie.cdnom_disparu AS d
            ON nc.cd_nom = d.cd_nom
    WHERE nc.cd_nom_remplacement IS NOT NULL
ON CONFLICT DO NOTHING ;
