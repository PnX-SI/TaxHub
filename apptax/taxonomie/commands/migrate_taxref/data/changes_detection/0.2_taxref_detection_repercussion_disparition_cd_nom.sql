-- ----------------------------------------------------------------------
-- Create temporary taxref schema
CREATE SCHEMA IF NOT EXISTS tmp_taxref_changes;

-- ----------------------------------------------------------------------
-- Add the cd_nom dependency search function
DROP FUNCTION IF EXISTS public.deps_test_fk_dependencies_cd_nom();
CREATE OR REPLACE FUNCTION public.deps_test_fk_dependencies_cd_nom()
    RETURNS void AS
$BODY$
    DECLARE
        v_curr record;
    BEGIN
        DROP TABLE IF EXISTS tmp_taxref_changes.dps_fk_cd_nom;

        CREATE TABLE  tmp_taxref_changes.dps_fk_cd_nom (
            cd_nom int,
            table_name varchar(250)
        );

        FOR v_curr IN (
            SELECT
                'SELECT DISTINCT
                    d.' || kcu.column_name || ' AS cd_nom, ''' ||
                    tc.table_schema || '.' ||  tc.table_name || ''' AS table
                FROM ' || tc.table_schema || '.' ||  tc.table_name || ' AS d
                    LEFT JOIN taxonomie.import_taxref AS it
                        ON it.cd_nom = d.' || kcu.column_name || '
                WHERE it.cd_nom IS NULL
                    AND d.' || kcu.column_name || ' IS NOT NULL ' AS SELECT,
                tc.table_schema,
                tc.table_name
            FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_catalog = kcu.constraint_catalog
                        AND tc.constraint_schema = kcu.constraint_schema
                        AND tc.constraint_name = kcu.constraint_name
                JOIN information_schema.referential_constraints rc
                    ON tc.constraint_catalog = rc.constraint_catalog
                        AND tc.constraint_schema = rc.constraint_schema
                        AND tc.constraint_name = rc.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON rc.unique_constraint_catalog = ccu.constraint_catalog
                        AND rc.unique_constraint_schema = ccu.constraint_schema
                        AND rc.unique_constraint_name = ccu.constraint_name
            WHERE lower(tc.constraint_type) IN ('foreign key')
                AND ccu.column_name = 'cd_nom' OR ccu.column_name = 'cd_ref'
        )
        LOOP
            EXECUTE 'INSERT INTO tmp_taxref_changes.dps_fk_cd_nom ' || v_curr.select;
        END LOOP;
    END
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100 ;
