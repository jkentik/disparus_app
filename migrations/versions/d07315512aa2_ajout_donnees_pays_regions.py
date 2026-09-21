"""ajout donnees pays regions

Revision ID: d07315512aa2
Revises: c1062cdb5114
Create Date: 2026-09-20

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d07315512aa2"
down_revision = "c1062cdb5114"
branch_labels = None
depends_on = None


def upgrade():

    countries = sa.table(
        "countries",
        sa.column("id", sa.Integer),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
    )

    regions = sa.table(
        "regions",
        sa.column("id", sa.Integer),
        sa.column("country_id", sa.Integer),
        sa.column("name", sa.String),
    )

    # =====================================================
    # PAYS
    # =====================================================

    op.bulk_insert(
        countries,
        [
            {"id": 1, "code": "BF", "name": "Burkina Faso"},
            {"id": 2, "code": "ML", "name": "Mali"},
            {"id": 3, "code": "CI", "name": "Côte d'Ivoire"},
            {"id": 4, "code": "NE", "name": "Niger"},
            {"id": 5, "code": "TG", "name": "Togo"},
            {"id": 6, "code": "BJ", "name": "Bénin"},
            {"id": 7, "code": "GH", "name": "Ghana"},
            {"id": 8, "code": "SN", "name": "Sénégal"},
        ],
    )

    # =====================================================
    # RÉGIONS DU BURKINA FASO
    # =====================================================

    op.bulk_insert(
        regions,
        [
            {"id": 1, "country_id": 1, "name": "Centre"},
            {"id": 2, "country_id": 1, "name": "Hauts-Bassins"},
            {"id": 3, "country_id": 1, "name": "Cascades"},
            {"id": 4, "country_id": 1, "name": "Boucle du Mouhoun"},
            {"id": 5, "country_id": 1, "name": "Centre-Est"},
            {"id": 6, "country_id": 1, "name": "Centre-Nord"},
            {"id": 7, "country_id": 1, "name": "Centre-Ouest"},
            {"id": 8, "country_id": 1, "name": "Centre-Sud"},
            {"id": 9, "country_id": 1, "name": "Est"},
            {"id": 10, "country_id": 1, "name": "Nord"},
            {"id": 11, "country_id": 1, "name": "Plateau-Central"},
            {"id": 12, "country_id": 1, "name": "Sahel"},
            {"id": 13, "country_id": 1, "name": "Sud-Ouest"},
        ],
    )


def downgrade():

    op.execute(
        "DELETE FROM regions WHERE country_id = 1"
    )

    op.execute(
        """
        DELETE FROM countries
        WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8)
        """
    )