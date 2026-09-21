from functools import wraps
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.authority import authority_bp
from app.extensions import db
from app.models.post import Post
from app.models.notification import Notification


def authority_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role not in ("authority", "admin"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def scoped_posts(base_query):
    """Filtre par région si l'agent en a une, sinon vue nationale (admin ou agent sans région)."""
    if current_user.role == "admin" or not current_user.region_id:
        return base_query
    return base_query.filter(Post.region_id == current_user.region_id)


@authority_bp.route("/")
@login_required
@authority_required
def index():
    posts = scoped_posts(Post.query.filter(Post.status == "active")).all()
    to_confirm = scoped_posts(Post.query.filter(Post.status == "retrouve_a_confirmer")).all()

    stats = {
        "personnes_disparues": sum(1 for p in posts if p.type == "personne_disparue"),
        "objets_recherches": sum(1 for p in posts if p.type == "objet_perdu"),
        "objets_retrouves": sum(1 for p in posts if p.type == "objet_retrouve"),
        "a_confirmer": len(to_confirm),
    }

    return render_template("authority/index.html", posts=posts, to_confirm=to_confirm, stats=stats)


@authority_bp.route("/search")
@login_required
@authority_required
def search():
    q = request.args.get("q", "")
    query = Post.query.filter(Post.title.ilike(f"%{q}%"))
    posts = scoped_posts(query).all()
    return render_template("authority/search.html", posts=posts, query=q)


@authority_bp.route("/posts/<int:post_id>/confirm-found", methods=["POST"])
@login_required
@authority_required
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
    return redirect(url_for("authority.index"))


@authority_bp.route("/posts/<int:post_id>/deny-found", methods=["POST"])
@login_required
@authority_required
def deny_found(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "active"
    post.finder_name = None
    post.finder_phone = None
    db.session.commit()
    flash("Appel non confirmé, signalement remis actif.")
    return redirect(url_for("authority.index"))