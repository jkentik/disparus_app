from app.extensions import db
from app.models.country import Country
from app.models.region import Region

DATA = {
    "BF": ("Burkina Faso", [
        "Boucle du Mouhoun", "Cascades", "Centre", "Centre-Est", "Centre-Nord",
        "Centre-Ouest", "Centre-Sud", "Est", "Hauts-Bassins", "Nord",
        "Plateau-Central", "Sahel", "Sud-Ouest"
    ]),
    "ML": ("Mali", [
        "Kayes", "Koulikoro", "Sikasso", "Ségou", "Mopti",
        "Tombouctou", "Gao", "Kidal", "Ménaka", "Taoudénit", "District de Bamako"
    ]),
    "NE": ("Niger", [
        "Agadez", "Diffa", "Dosso", "Maradi", "Tahoua", "Tillabéri", "Zinder", "Niamey"
    ]),
    "CI": ("Côte d'Ivoire", [
        "Abidjan", "Bas-Sassandra", "Comoé", "Denguélé", "Gôh-Djiboua",
        "Lacs", "Lagunes", "Montagnes", "Sassandra-Marahoué", "Savanes",
        "Vallée du Bandama", "Woroba", "Zanzan"
    ]),
    "SN": ("Sénégal", [
        "Dakar", "Diourbel", "Fatick", "Kaffrine", "Kaolack", "Kédougou",
        "Kolda", "Louga", "Matam", "Saint-Louis", "Sédhiou", "Tambacounda",
        "Thiès", "Ziguinchor"
    ]),
    "TG": ("Togo", ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]),
    "BJ": ("Bénin", [
        "Alibori", "Atacora", "Atlantique", "Borgou", "Collines", "Couffo",
        "Donga", "Littoral", "Mono", "Ouémé", "Plateau", "Zou"
    ]),
    "GN": ("Guinée", [
        "Boké", "Conakry", "Faranah", "Kankan", "Kindia", "Labé", "Mamou", "Nzérékoré"
    ]),
    "GH": ("Ghana", [
        "Greater Accra", "Ashanti", "Western", "Eastern", "Central",
        "Volta", "Northern", "Upper East", "Upper West", "Bono"
    ]),
}


def seed_countries_and_regions():
    for code, (name, regions) in DATA.items():
        country = Country.query.filter_by(code=code).first()
        if not country:
            country = Country(code=code, name=name)
            db.session.add(country)
            db.session.flush()  # pour avoir country.id tout de suite

        for region_name in regions:
            exists = Region.query.filter_by(country_id=country.id, name=region_name).first()
            if not exists:
                db.session.add(Region(country_id=country.id, name=region_name))

    db.session.commit()
    print("Pays et régions insérés avec succès.")