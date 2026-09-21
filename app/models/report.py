from datetime import datetime
from app.extensions import db

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="en_attente")  # en_attente, traite, rejete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship("Post")
    reporter = db.relationship("User")