import secrets
from datetime import datetime
from app.extensions import db


def generate_code():
    """Génère un code du type A7F3-9K2L."""
    raw = secrets.token_hex(4).upper()  # 8 caractères hexa
    return f"{raw[:4]}-{raw[4:]}"


class AuthorityInvite(db.Model):
    __tablename__ = "authority_invites"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, default=generate_code)

    agency_name = db.Column(db.String(150))  # ex: "Police nationale - Ouaga"

    # Champs facultatifs : si vous voulez pré-assigner une région précise
    # au code (sinon l'autorité choisira son pays/région au moment de l'inscription).
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)

    def is_valid(self):
        if self.used:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True