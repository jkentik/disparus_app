from app.extensions import db

class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)   # ISO ex: BF, ML, CI
    name = db.Column(db.String(100), nullable=False)

    regions = db.relationship("Region", backref="country")