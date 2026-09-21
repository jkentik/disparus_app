import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.country import Country
from app.models.region import Region
from app.models.authority_invite import AuthorityInvite

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        country_id = request.form.get("country_id")

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.")
            return redirect(url_for("auth.register"))

        user = User(name=name, email=email, country_id=country_id or None)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès, connecte-toi.")
        return redirect(url_for("auth.login"))

    countries = Country.query.order_by(Country.name).all()
    return render_template("auth/register.html", countries=countries)


@auth_bp.route("/register-authority", methods=["GET", "POST"])
def register_authority():
    code_value = request.args.get("code") or request.form.get("code")
    invite = AuthorityInvite.query.filter_by(code=code_value).first() if code_value else None

    if not invite or not invite.is_valid():
        flash("Ce lien d'invitation est invalide ou a déjà été utilisé.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        country_id = invite.country_id or request.form.get("country_id")
        region_id = invite.region_id or request.form.get("region_id")

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.")
            return redirect(url_for("auth.register_authority", code=code_value))

        user = User(
            name=name,
            email=email,
            role="authority",
            country_id=country_id or None,
            region_id=region_id or None,
        )
        user.set_password(password)
        db.session.add(user)

        invite.used = True
        invite.used_at = datetime.utcnow()
        db.session.commit()

        invite.used_by = user.id
        db.session.commit()

        flash("Compte autorité créé. Vous pouvez vous connecter.")
        return redirect(url_for("auth.login"))

    countries = Country.query.order_by(Country.name).all()
    regions = Region.query.order_by(Region.name).all()
    return render_template(
        "auth/register_authority.html",
        invite=invite,
        code=code_value,
        countries=countries,
        regions=regions,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("posts.index"))

        flash("Email ou mot de passe incorrect.")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    user = current_user
    Post.query.filter_by(user_id=user.id).delete()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Ton compte et tes signalements ont été supprimés.")
    return redirect(url_for("posts.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    my_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return render_template("auth/profile.html", user=current_user, posts=my_posts)


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.country_id = request.form.get("country_id") or None

        photo = request.files.get("photo")
        if photo and photo.filename != "":
            if not allowed_file(photo.filename):
                flash("Format de photo non autorisé (jpg, jpeg, png, gif uniquement).")
                return redirect(url_for("auth.edit_profile"))

            filename = secure_filename(f"user_{current_user.id}_{photo.filename}")
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            photo.save(os.path.join(upload_folder, filename))
            current_user.photo = filename

        db.session.commit()
        flash("Profil mis à jour.")
        return redirect(url_for("auth.profile"))

    countries = Country.query.order_by(Country.name).all()
    return render_template("auth/edit_profile.html", countries=countries)