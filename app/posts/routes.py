import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.posts import posts_bp
from app.extensions import db
from app.models.post import Post
from app.models.category import Category
from app.models.notification import Notification
from app.models.country import Country
from app.models.region import Region
from app.models.match import Match
from app.models.report import Report
from app.models.user import User
from app.models.post_follow import PostFollow

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@posts_bp.route("/")
def index():
    cat = request.args.get("cat", "tous")
    query = Post.query.filter_by(status="active")

    if current_user.is_authenticated and current_user.country_id:
        query = query.filter(
            (Post.country_id == current_user.country_id) | (Post.is_international == True)
        )

    if cat == "disparitions":
        query = query.filter(Post.type == "personne_disparue")
    elif cat == "objets":
        query = query.filter(Post.type == "objet_perdu")
    elif cat == "retrouves":
        query = query.filter(Post.type.in_(["objet_retrouve", "personne_retrouvee"]))

    recent_posts = query.order_by(Post.created_at.desc()).limit(20).all()
    return render_template("posts/index.html", posts=recent_posts, cat=cat)


@posts_bp.route("/posts/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        photo_filename = None
        photo = request.files.get("photo")

        if photo and photo.filename != "":
            if not allowed_file(photo.filename):
                flash("Format de photo non autorisé (jpg, jpeg, png, gif uniquement).")
                return redirect(url_for("posts.create"))

            filename = secure_filename(photo.filename)
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            photo.save(os.path.join(upload_folder, filename))
            photo_filename = filename

        requested_international = request.form.get("request_international") == "1"

        post = Post(
            user_id=current_user.id,
            type=request.form.get("type"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            location=request.form.get("location"),
            photo=photo_filename,
            brand=request.form.get("brand"),
            color=request.form.get("color"),
            country_id=request.form.get("country_id") or current_user.country_id,
            region_id=request.form.get("region_id") or None,
            is_international=False,
            international_requested=requested_international,
            latitude=request.form.get("latitude") or None,
            longitude=request.form.get("longitude") or None,
        )
        db.session.add(post)
        db.session.commit()
        flash("Signalement publié. Il sera visible après validation par un administrateur.")
        return redirect(url_for("posts.index"))

    categories = Category.query.all()
    countries = Country.query.order_by(Country.name).all()
    regions = Region.query.order_by(Region.name).all()
    return render_template("posts/create.html", categories=categories, countries=countries, regions=regions)


import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


@posts_bp.route("/posts/search")
def search():
    q = request.args.get("q", "")
    type_filter = request.args.get("type", "tous")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    query = Post.query.filter(
        Post.title.ilike(f"%{q}%"),
        Post.status == "active"
    )

    if current_user.is_authenticated and current_user.country_id:
        query = query.filter(
            (Post.country_id == current_user.country_id) | (Post.is_international == True)
        )

    if type_filter == "disparitions":
        query = query.filter(Post.type == "personne_disparue")
    elif type_filter == "objets":
        query = query.filter(Post.type == "objet_perdu")
    elif type_filter == "retrouves":
        query = query.filter(Post.type.in_(["objet_retrouve", "personne_retrouvee"]))

    if date_from:
        query = query.filter(Post.date_event >= date_from)
    if date_to:
        query = query.filter(Post.date_event <= date_to)

    posts = query.all()

    if lat is not None and lng is not None:
        posts_with_coords = [p for p in posts if p.latitude is not None and p.longitude is not None]
        for p in posts_with_coords:
            p.distance_km = haversine_km(lat, lng, p.latitude, p.longitude)
        posts = sorted(posts_with_coords, key=lambda p: p.distance_km)
        posts = [p for p in posts if p.distance_km <= 100]  # rayon 100 km

    return render_template(
        "posts/search.html",
        posts=posts,
        query=q,
        type_filter=type_filter,
        date_from=date_from,
        date_to=date_to,
        lat=lat,
        lng=lng,
    )


@posts_bp.route("/posts/<int:post_id>")
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    post.views_count = (post.views_count or 0) + 1
    db.session.commit()
    matches = Match.query.filter(
        (Match.post_id_1 == post_id) | (Match.post_id_2 == post_id)
    ).order_by(Match.score.desc()).all()
    return render_template("posts/detail.html", post=post, matches=matches)


@posts_bp.route("/posts/<int:post_id>/mark-found", methods=["POST"])
@login_required
def mark_found(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("Tu ne peux modifier que tes propres signalements.")
        return redirect(url_for("posts.detail", post_id=post.id))

    post.status = "retrouvee"

    notification = Notification(
        user_id=current_user.id,
        post_id=post.id,
        message=f"Ton signalement « {post.title} » a été marqué comme retrouvé."
    )
    db.session.add(notification)
    db.session.commit()

    followers = PostFollow.query.filter_by(post_id=post.id).all()
    for follow_entry in followers:
        if follow_entry.user_id == current_user.id:
            continue
        db.session.add(Notification(
            user_id=follow_entry.user_id,
            post_id=post.id,
            message=f"Bonne nouvelle : « {post.title} » a été marqué comme retrouvé."
        ))
    db.session.commit()

    flash("Signalement marqué comme retrouvé.")
    return redirect(url_for("posts.detail", post_id=post.id))


@posts_bp.route("/posts/<int:post_id>/follow", methods=["POST"])
@login_required
def follow(post_id):
    post = Post.query.get_or_404(post_id)
    existing = PostFollow.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Vous ne suivez plus ce signalement.")
    else:
        db.session.add(PostFollow(user_id=current_user.id, post_id=post.id))
        db.session.commit()
        flash("Vous suivrez les mises à jour de ce signalement.")

    return redirect(url_for("posts.detail", post_id=post.id))


@posts_bp.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("Tu ne peux supprimer que tes propres signalements.")
        return redirect(url_for("posts.detail", post_id=post.id))

    db.session.delete(post)
    db.session.commit()
    flash("Signalement supprimé.")
    return redirect(url_for("posts.index"))


@posts_bp.route("/posts/<int:post_id>/report-found", methods=["GET", "POST"])
def report_found(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.finder_name = request.form.get("finder_name")
        post.finder_phone = request.form.get("finder_phone")
        post.status = "retrouve_a_confirmer"
        db.session.commit()
        flash("Merci. La police va vous appeler pour confirmer avant de clôturer ce signalement.")
        return redirect(url_for("posts.detail", post_id=post.id))

    return render_template("posts/report_found.html", post=post)


@posts_bp.route("/users/<int:user_id>")
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id, status="active").order_by(Post.created_at.desc()).all()
    return render_template("posts/public_profile.html", profile_user=user, posts=posts)


@posts_bp.route("/carte")
def map_view():
    return render_template("posts/map.html")


@posts_bp.route("/api/posts/map")
def map_data():
    query = Post.query.filter(
        Post.status == "active",
        Post.latitude.isnot(None),
        Post.longitude.isnot(None),
    )
    if current_user.is_authenticated and current_user.country_id:
        query = query.filter(
            (Post.country_id == current_user.country_id) | (Post.is_international == True)
        )
    posts = query.all()
    data = [
        {"id": p.id, "title": p.title, "type": p.type, "lat": p.latitude, "lng": p.longitude}
        for p in posts
    ]
    return jsonify(data)


@posts_bp.route("/posts/<int:post_id>/report", methods=["GET", "POST"])
@login_required
def report_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        report = Report(
            post_id=post.id,
            reporter_id=current_user.id,
            reason=request.form.get("reason"),
        )
        db.session.add(report)
        db.session.commit()
        flash("Merci, la modération va examiner ce signalement.")
        return redirect(url_for("posts.detail", post_id=post.id))
    return render_template("posts/report_post.html", post=post)