from functools import wraps
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.extensions import db
from app.models.post import Post
from app.models.notification import Notification
from app.models.authority_invite import AuthorityInvite
from app.models.country import Country
from app.models.region import Region
from app.models.user import User
from app.matching import find_matches_for_post


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def index():
    pending_posts = Post.query.filter_by(status="en_attente").order_by(Post.created_at.asc()).all()
    to_confirm = Post.query.filter_by(status="retrouve_a_confirmer").order_by(Post.created_at.asc()).all()
    return render_template("admin/index.html", posts=pending_posts, to_confirm=to_confirm)


@admin_bp.route("/posts/<int:post_id>/validate", methods=["POST"])
@login_required
@admin_required
def validate(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "active"
    db.session.commit()

    matches = find_matches_for_post(post)
    for match in matches:
        other_post = match.post_2 if match.post_id_1 == post.id else match.post_1
        for p in [post, other_post]:
            notification = Notification(
                user_id=p.user_id,
                post_id=p.id,
                message=f"Une correspondance potentielle ({match.level}) a été trouvée pour « {p.title} »."
            )
            db.session.add(notification)
    db.session.commit()

    flash(f"Signalement validé. {len(matches)} correspondance(s) potentielle(s) trouvée(s).")
    return redirect(url_for("admin.index"))


@admin_bp.route("/posts/<int:post_id>/reject", methods=["POST"])
@login_required
@admin_required
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
    return redirect(url_for("admin.index"))


@admin_bp.route("/posts/<int:post_id>/confirm-found", methods=["POST"])
@login_required
@admin_required
def confirm_found(post_id):
    post = Post.query.get_or_404(post_id)

    notification = Notification(
        user_id=post.user_id,
        post_id=None,
        message=f"Ton signalement « {post.title} » a été confirmé retrouvé après vérification téléphonique."
    )
    db.session.add(notification)
    db.session.delete(post)
    db.session.commit()
    flash("Signalement confirmé retrouvé et clôturé.")
    return redirect(url_for("admin.index"))


@admin_bp.route("/posts/<int:post_id>/deny-found", methods=["POST"])
@login_required
@admin_required
def deny_found(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "active"
    post.finder_name = None
    post.finder_phone = None
    db.session.commit()
    flash("Appel non confirmé, signalement remis actif.")
    return redirect(url_for("admin.index"))


@admin_bp.route("/posts/<int:post_id>/set-international", methods=["POST"])
@login_required
@admin_required
def set_international(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_international = True
    db.session.commit()
    flash("Signalement diffusé internationalement.")
    return redirect(url_for("admin.index"))


@admin_bp.route("/authority-invites", methods=["GET", "POST"])
@login_required
@admin_required
def authority_invites():
    if request.method == "POST":
        agency_name = request.form.get("agency_name")
        country_id = request.form.get("country_id") or None
        region_id = request.form.get("region_id") or None
        expires_days = request.form.get("expires_days")

        invite = AuthorityInvite(
            agency_name=agency_name,
            country_id=country_id,
            region_id=region_id,
            created_by=current_user.id,
            expires_at=(
                datetime.utcnow() + timedelta(days=int(expires_days))
                if expires_days else None
            ),
        )
        db.session.add(invite)
        db.session.commit()
        flash(f"Code généré : {invite.code}")
        return redirect(url_for("admin.authority_invites"))

    countries = Country.query.order_by(Country.name).all()
    regions = Region.query.order_by(Region.name).all()
    invites = AuthorityInvite.query.order_by(AuthorityInvite.created_at.desc()).all()

    return render_template(
        "admin/authority_invites.html",
        countries=countries,
        regions=regions,
        invites=invites,
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()

    stats = {
        "total_users": User.query.count(),
        "total_authorities": User.query.filter_by(role="authority").count(),
        "posts_active": Post.query.filter_by(status="active").count(),
        "posts_resolved": Post.query.filter_by(status="retrouvee").count(),
    }

    return render_template("admin/users.html", users=all_users, stats=stats)