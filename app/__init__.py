from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager
from app.models import (
    User,
    Category,
    Post,
    Notification,
    Match,
    Country,
    Region,
    Message,
    Report,
)


def create_admin(app):
    """
    Crée le compte administrateur s'il n'existe pas encore.

    Les identifiants doivent être fournis dans les variables
    d'environnement ADMIN_EMAIL et ADMIN_PASSWORD.
    """

    import os

    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return

    with app.app_context():

        # Si l'admin existe déjà, on ne fait rien.
        admin = User.query.filter_by(email=admin_email).first()

        if admin:
            return

        admin = User(
            name="Administrateur",
            email=admin_email,
            role="admin",
            status="active",
        )

        admin.set_password(admin_password)

        db.session.add(admin)
        db.session.commit()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.posts import posts_bp
    app.register_blueprint(posts_bp)

    from app.notifications import notifications_bp
    app.register_blueprint(notifications_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.messages import messages_bp
    app.register_blueprint(messages_bp)

    from app.moderation import moderation_bp
    app.register_blueprint(moderation_bp)

    from app.authority import authority_bp
    app.register_blueprint(authority_bp)

    return app