from datetime import datetime
from app.extensions import db

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    date_event = db.Column(db.Date)
    photo = db.Column(db.String(255))
    status = db.Column(db.String(20), default="en_attente")
    priority = db.Column(db.String(10), default="normal")

    finder_name = db.Column(db.String(100))
    finder_phone = db.Column(db.String(30))

    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=True)
    is_international = db.Column(db.Boolean, default=False)
    international_requested = db.Column(db.Boolean, default=False)

    views_count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="posts")
    category = db.relationship("Category", backref="posts")
    country = db.relationship("Country")
    region = db.relationship("Region")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)