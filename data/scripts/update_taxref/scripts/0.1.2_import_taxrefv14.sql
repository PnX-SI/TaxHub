-- Importer les données depuis les CSV.
-- Attention l'utilisateur qui exécute ce script doit être superuser
BEGIN;
COPY taxonomie.import_taxref FROM  '/tmp/taxhub/TAXREF_v14_2020/TAXREFv14.txt'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

COPY taxonomie.cdnom_disparu FROM  '/tmp/taxhub/TAXREF_v14_2020/CDNOM_DISPARUS.csv'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

COPY taxonomie.taxref_changes FROM  '/tmp/taxhub/TAXREF_v14_2020/TAXREF_CHANGES.txt'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';


COPY taxonomie.import_taxref_rangs FROM  '/tmp/taxhub/TAXREF_v14_2020/rangs_note.csv'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

END;
