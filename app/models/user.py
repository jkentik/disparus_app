from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    photo = db.Column(db.String(255))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")       # user, moderator, authority, business, admin
    status = db.Column(db.String(20), default="active")   # active, suspended, deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=True)

    country = db.relationship("Country", foreign_keys=[country_id])
    region = db.relationship("Region", foreign_keys=[region_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))