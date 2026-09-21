from functools import wraps
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.moderation import moderation_bp
from app.extensions import db
from app.models.post import Post
from app.models.report import Report
from app.models.notification import Notification
from app.matching import find_matches_for_post


def moderator_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role not in ("moderator", "admin"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@moderation_bp.route("/")
@login_required
@moderator_required
def index():
    pending_posts = Post.query.filter_by(status="en_attente").order_by(Post.created_at.asc()).all()
    open_reports = Report.query.filter_by(status="en_attente").order_by(Report.created_at.asc()).all()
    return render_template("moderation/index.html", posts=pending_posts, reports=open_reports)


@moderation_bp.route("/posts/<int:post_id>/validate", methods=["POST"])
@login_required
@moderator_required
def validate(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "active"
    db.session.commit()
    find_matches_for_post(post)
    flash("Signalement validé.")
    return redirect(url_for("moderation.index"))


@moderation_bp.route("/posts/<int:post_id>/reject", methods=["POST"])
@login_required
@moderator_required
def reject(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "refusee"
    notification = Notification(
        user_id=post.user_id,
        post_id=post.id,
        message=f"Ton signalement « {post.title} » a été refusé par la modération."
    )
    db.session.add(notification)
    db.session.commit()
    flash("Signalement refusé.")
    return redirect(url_for("moderation.index"))


@moderation_bp.route("/reports/<int:report_id>/hide-post", methods=["POST"])
@login_required
@moderator_required
def hide_post(report_id):
    report = Report.query.get_or_404(report_id)
    report.post.status = "suspendue"
    report.status = "traite"
    db.session.commit()
    flash("Publication suspendue suite au signalement.")
    return redirect(url_for("moderation.index"))


@moderation_bp.route("/reports/<int:report_id>/dismiss", methods=["POST"])
@login_required
@moderator_required
def dismiss_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = "rejete"
    db.session.commit()
    flash("Signalement rejeté, publication conservée.")
    return redirect(url_for("moderation.index"))