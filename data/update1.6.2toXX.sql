CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_attributesviews_per_kingdom()
  RETURNS trigger AS
$BODY$
DECLARE
   sregne text;
   lregne text;
BEGIN
    RAISE NOTICE '%', TG_OP;
    IF TG_OP = 'DELETE' OR TG_OP = 'TRUNCATE' THEN
        sregne := OLD.regne;
    ELSE
        sregne := NEW.regne;
    END IF;

    IF sregne IS NULL THEN
        FOR lregne IN
            SELECT DISTINCT regne
            FROM taxonomie.taxref t
            JOIN taxonomie.bib_noms n
            ON t.cd_nom = n.cd_nom
            WHERE t.regne IS NOT NULL
        LOOP
            PERFORM taxonomie.fct_build_bibtaxon_attributs_view(lregne);
        END LOOP;
    ELSE
        PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
    END IF;
    
    IF TG_OP = 'DELETE' OR TG_OP = 'TRUNCATE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
    
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
