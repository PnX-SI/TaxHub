"""Create bdc_status_table if not exists

Revision ID: 23c25552d707
Revises: 188bc535258a
Create Date: 2023-03-16 17:13:34.498089

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "23c25552d707"
down_revision = "188bc535258a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS taxonomie.bdc_statut (
            id serial,
            cd_nom int NOT NULL,
            cd_ref int NOT NULL,
            cd_sup int,
            cd_type_statut varchar(50) NOT NULL,
            lb_type_statut varchar(250),
            regroupement_type varchar(250),
            code_statut varchar(250),
            label_statut varchar(1000),
            rq_statut text,
            cd_sig varchar(100),
            cd_doc int,
            lb_nom varchar(1000),
            lb_auteur varchar(1000),
            nom_complet_html varchar(1000),
            nom_valide_html varchar(1000),
            regne varchar(250),
            phylum varchar(250),
            classe varchar(250),
            ordre varchar(250),
            famille varchar(250),
            group1_inpn varchar(255),
            group2_inpn varchar(255),
            lb_adm_tr varchar(100),
            niveau_admin varchar(250),
            cd_iso3166_1 varchar(50),
            cd_iso3166_2 varchar(50),
            full_citation text,
            doc_url text,
            thematique varchar(100),
            type_value varchar(100)
        );

        CREATE INDEX IF NOT EXISTS bdc_statut_id_idx ON taxonomie.bdc_statut (id);
    """
    )


def downgrade():
    """Pas de downgrade car on souhaite s'assurer de la création de la table
    sur toute les instances
    """
    pass
