"""delete bib_noms dependancies (cor_nom_liste)

Revision ID: b7d734f490ff
Revises: 64d38dbe7739
Create Date: 2022-11-22 16:50:15.520049

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7d734f490ff"
down_revision = "8f3256f60915"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.cor_nom_liste ADD cd_nom int;

        UPDATE taxonomie.cor_nom_liste AS cnl SET  cd_nom = bn.cd_nom
        FROM taxonomie.bib_noms AS bn
        WHERE bn.id_nom = cnl.id_nom;

        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT unique_cor_nom_liste_id_liste_id_nom;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_noms_fkey;

        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY (cd_nom, id_liste);
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT unique_cor_nom_liste_id_liste_cd_nom UNIQUE (id_liste, cd_nom);
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_taxref_fkey FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom) ON DELETE CASCADE ON UPDATE CASCADE;


        ALTER TABLE taxonomie.cor_nom_liste ALTER COLUMN id_nom DROP NOT NULL;

         CREATE OR REPLACE VIEW taxonomie.v_taxref_all_listes AS
         SELECT t.regne,
            t.phylum,
            t.classe,
            t.ordre,
            t.famille,
            t.group1_inpn,
            t.group2_inpn,
            t.cd_nom,
            t.cd_ref,
            t.nom_complet,
            t.nom_valide,
            t.nom_vern AS nom_vern,
            t.lb_nom,
            d.id_liste
         FROM taxonomie.taxref t
         JOIN taxonomie.cor_nom_liste d ON t.cd_nom = d.cd_nom;


         ALTER TABLE  taxonomie.t_medias DROP CONSTRAINT fk_t_media_bib_noms;
         ALTER TABLE  taxonomie.t_medias ADD CONSTRAINT fk_t_media_bib_noms FOREIGN KEY (cd_ref)
         REFERENCES taxonomie.taxref(cd_nom) ON UPDATE CASCADE;

         DROP VIEW taxonomie.v_taxref_hierarchie_bibtaxons;

        ALTER TABLE taxonomie.cor_nom_liste DROP id_nom;

        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.cor_nom_liste ADD id_nom int;

        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey;

         ALTER TABLE ONLY taxonomie.cor_nom_liste
            ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY (id_nom, id_liste);

        ALTER TABLE taxonomie.cor_nom_liste
         ADD CONSTRAINT unique_cor_nom_liste_id_liste_id_nom
         UNIQUE (id_liste, id_nom);

         ALTER TABLE ONLY taxonomie.cor_nom_liste
            ADD CONSTRAINT cor_nom_listes_bib_noms_fkey FOREIGN KEY (id_nom)
            REFERENCES taxonomie.bib_noms(id_nom);

        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT unique_cor_nom_liste_id_liste_cd_nom;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_taxref_fkey;

 CREATE OR REPLACE VIEW taxonomie.v_taxref_all_listes
    AS WITH bib_nom_lst AS (
            SELECT cor_nom_liste.id_nom,
                bib_noms.cd_nom,
                bib_noms.nom_francais,
                cor_nom_liste.id_liste
            FROM taxonomie.cor_nom_liste
                JOIN taxonomie.bib_noms USING (id_nom)
            )
    SELECT t.regne,
        t.phylum,
        t.classe,
        t.ordre,
        t.famille,
        t.group1_inpn,
        t.group2_inpn,
        t.cd_nom,
        t.cd_ref,
        t.nom_complet,
        t.nom_valide,
        d.nom_francais AS nom_vern,
        t.lb_nom,
        d.id_liste
    FROM taxonomie.taxref t
        JOIN bib_nom_lst d ON t.cd_nom = d.cd_nom;

    ALTER TABLE  taxonomie.t_medias DROP CONSTRAINT fk_t_media_bib_noms;
    ALTER TABLE  taxonomie.t_medias ADD CONSTRAINT fk_t_media_bib_noms FOREIGN KEY (cd_ref)
    REFERENCES taxonomie.bib_noms(cd_nom) ON UPDATE CASCADE;

    -- taxonomie.v_taxref_hierarchie_bibtaxons source

    CREATE OR REPLACE VIEW taxonomie.v_taxref_hierarchie_bibtaxons
    AS WITH mestaxons AS (
            SELECT tx_1.cd_nom,
            tx_1.id_statut,
            tx_1.id_habitat,
            tx_1.id_rang,
            tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille,
            tx_1.cd_taxsup,
            tx_1.cd_sup,
            tx_1.cd_ref,
            tx_1.lb_nom,
            tx_1.lb_auteur,
            tx_1.nom_complet,
            tx_1.nom_complet_html,
            tx_1.nom_valide,
            tx_1.nom_vern,
            tx_1.nom_vern_eng,
            tx_1.group1_inpn,
            tx_1.group2_inpn
            FROM taxonomie.taxref tx_1
                JOIN taxonomie.bib_noms t ON t.cd_nom = tx_1.cd_nom
        )
    SELECT DISTINCT tx.regne,
    tx.phylum,
    tx.classe,
    tx.ordre,
    tx.famille,
    tx.cd_nom,
    tx.cd_ref,
    tx.lb_nom,
    btrim(tx.id_rang::text) AS id_rang,
    f.nb_tx_fm,
    o.nb_tx_or,
    c.nb_tx_cl,
    p.nb_tx_ph,
    r.nb_tx_kd
    FROM taxonomie.taxref tx
        JOIN ( SELECT DISTINCT tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille
            FROM mestaxons tx_1) a ON a.regne::text = tx.regne::text AND tx.id_rang::text = 'KD'::text OR a.phylum::text = tx.phylum::text AND tx.id_rang::text = 'PH'::text OR a.classe::text = tx.classe::text AND tx.id_rang::text = 'CL'::text OR a.ordre::text = tx.ordre::text AND tx.id_rang::text = 'OR'::text OR a.famille::text = tx.famille::text AND tx.id_rang::text = 'FM'::text
        LEFT JOIN ( SELECT mestaxons.famille,
            count(*) AS nb_tx_fm
            FROM mestaxons
            WHERE mestaxons.id_rang::text <> 'FM'::text
            GROUP BY mestaxons.famille) f ON f.famille::text = tx.famille::text
        LEFT JOIN ( SELECT mestaxons.ordre,
            count(*) AS nb_tx_or
            FROM mestaxons
            WHERE mestaxons.id_rang::text <> 'OR'::text
            GROUP BY mestaxons.ordre) o ON o.ordre::text = tx.ordre::text
        LEFT JOIN ( SELECT mestaxons.classe,
            count(*) AS nb_tx_cl
            FROM mestaxons
            WHERE mestaxons.id_rang::text <> 'CL'::text
            GROUP BY mestaxons.classe) c ON c.classe::text = tx.classe::text
        LEFT JOIN ( SELECT mestaxons.phylum,
            count(*) AS nb_tx_ph
            FROM mestaxons
            WHERE mestaxons.id_rang::text <> 'PH'::text
            GROUP BY mestaxons.phylum) p ON p.phylum::text = tx.phylum::text
        LEFT JOIN ( SELECT mestaxons.regne,
            count(*) AS nb_tx_kd
            FROM mestaxons
            WHERE mestaxons.id_rang::text <> 'KD'::text
            GROUP BY mestaxons.regne) r ON r.regne::text = tx.regne::text
    WHERE (tx.id_rang::text = ANY (ARRAY['KD'::character varying::text, 'PH'::character varying::text, 'CL'::character varying::text, 'OR'::character varying::text, 'FM'::character varying::text])) AND tx.cd_nom = tx.cd_ref;

        ALTER TABLE taxonomie.cor_nom_liste DROP cd_nom;


        """
    )
