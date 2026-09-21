"""ajout des données pays et régions

Revision ID: seed_countries_regions
Revises: c1062cdb5114
"""

from alembic import op
import sqlalchemy as sa


revision = "seed_countries_regions"
down_revision = "c1062cdb5114"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

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

    # Pays
    country_data = [
        {"id": 1, "code": "BF", "name": "Burkina Faso"},
        {"id": 2, "code": "ML", "name": "Mali"},
        {"id": 3, "code": "CI", "name": "Côte d'Ivoire"},
        {"id": 4, "code": "NE", "name": "Niger"},
        {"id": 5, "code": "TG", "name": "Togo"},
        {"id": 6, "code": "BJ", "name": "Bénin"},
        {"id": 7, "code": "GH", "name": "Ghana"},
        {"id": 8, "code": "SN", "name": "Sénégal"},
    ]

    existing_countries = {
        row[0]
        for row in conn.execute(
            sa.select(countries.c.code)
        ).fetchall()
    }

    for country in country_data:
        if country["code"] not in existing_countries:
            conn.execute(countries.insert().values(**country))

    # Régions / provinces principales
    region_data = [
        (1, 1, "Centre"),
        (2, 1, "Hauts-Bassins"),
        (3, 1, "Cascades"),
        (4, 1, "Boucle du Mouhoun"),
        (5, 1, "Centre-Est"),
        (6, 1, "Centre-Nord"),
        (7, 1, "Centre-Ouest"),
        (8, 1, "Centre-Sud"),
        (9, 1, "Est"),
        (10, 1, "Nord"),
        (11, 1, "Plateau-Central"),
        (12, 1, "Sahel"),
        (13, 1, "Sud-Ouest"),
    ]

    for region_id, country_id, name in region_data:
        exists = conn.execute(
            sa.select(regions.c.id)
            .where(regions.c.country_id == country_id)
            .where(regions.c.name == name)
        ).first()

        if not exists:
            conn.execute(
                regions.insert().values(
                    id=region_id,
                    country_id=country_id,
                    name=name,
                )
            )


def downgrade():
    conn = op.get_bind()

    conn.execute(
        sa.text(
            "DELETE FROM regions "
            "WHERE country_id = 1"
        )
    )

    conn.execute(
        sa.text(
            "DELETE FROM countries "
            "WHERE code IN "
            "('BF','ML','CI','NE','TG','BJ','GH','SN')"
        )
    )