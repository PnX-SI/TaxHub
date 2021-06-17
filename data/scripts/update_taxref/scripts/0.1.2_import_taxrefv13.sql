-- Importer les données depuis les CSV. 
-- Attention l'utilisateur qui exécute ce script doit être superuser
COPY taxonomie.import_taxref FROM  '/tmp/taxhub/TAXREF_INPN_v13/TAXREFv13.txt'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

COPY taxonomie.cdnom_disparu FROM  '/tmp/taxhub/TAXREF_INPN_v13/CDNOM_DISPARUS.csv'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

DELETE FROM taxonomie.taxref_changes;
COPY taxonomie.taxref_changes FROM  '/tmp/taxhub/TAXREF_INPN_v13/TAXREF_CHANGES.txt'
WITH  CSV HEADER
DELIMITER E'\t'  encoding 'UTF-8';

