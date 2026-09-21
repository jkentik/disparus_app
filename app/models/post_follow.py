from datetime import datetime
from app.extensions import db


class PostFollow(db.Model):
    __tablename__ = "post_follows"
    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="uq_post_follow_user_post"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
    post = db.relationship(
        "Post",
        backref=db.backref("follows", cascade="all, delete-orphan")
    )