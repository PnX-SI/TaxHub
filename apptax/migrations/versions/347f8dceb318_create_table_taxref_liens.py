"""Create table TAXREF_LIENS

Revision ID: 347f8dceb318
Revises: da3172cecdb1
Create Date: 2025-03-17 10:05:58.613859

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "347f8dceb318"
down_revision = "da3172cecdb1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """                
        CREATE TABLE taxonomie.taxref_liens ( 
            ct_name varchar(250) NOT NULL, -- Acronyme de la base d'origine
            ct_type  varchar(250) NOT NULL,-- Portée de la base (mondiale, régionale, locale)
            ct_authors text NULL,  -- Auteurs de la base
            ct_title varchar NULL, -- Nom complet de la base d'origine
            ct_url varchar(250) NULL, -- url de la source
            cd_nom int NOT NULL REFERENCES taxonomie.taxref (cd_nom),
            ct_sp_id varchar NULL, --identifiant du taxon dans la base d'origine
            url_sp text NULL, --url de la fiche du taxon dans la base d'origine
            CONSTRAINT taxref_liens_pkey PRIMARY KEY (ct_name, cd_nom, ct_sp_id)
        );
    """
    )


def downgrade():
    op.execute("DROP TABLE taxonomie.taxref_liens;")
