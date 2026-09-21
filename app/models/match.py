from datetime import datetime
from app.extensions import db

class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    post_id_1 = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    post_id_2 = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    level = db.Column(db.String(20), nullable=False)   # moyenne, elevee
    status = db.Column(db.String(20), default="proposee")  # proposee, confirmee, rejetee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post_1 = db.relationship("Post", foreign_keys=[post_id_1])
    post_2 = db.relationship("Post", foreign_keys=[post_id_2])