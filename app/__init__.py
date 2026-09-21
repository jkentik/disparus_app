from dotenv import load_dotenv

load_dotenv()

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
    Crée automatiquement le compte administrateur
    s'il n'existe pas encore.

    Les identifiants sont récupérés depuis :
    ADMIN_EMAIL
    ADMIN_PASSWORD
    """

    import os

    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    # Si les variables ne sont pas définies,
    # on ne crée rien.
    if not admin_email or not admin_password:
        return

    with app.app_context():

        # Vérifier si l'admin existe déjà
        admin = User.query.filter_by(
            email=admin_email
        ).first()

        if admin:
            return

        # Créer le compte admin
        admin = User(
            name="Administrateur",
            email=admin_email,
            role="admin",
            status="active",
        )

        # Le mot de passe est correctement hashé
        admin.set_password(admin_password)

        db.session.add(admin)
        db.session.commit()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # =====================================================
    # EXTENSIONS
    # =====================================================

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    # =====================================================
    # AUTH
    # =====================================================

    from app.auth import auth_bp

    app.register_blueprint(auth_bp)

    # =====================================================
    # POSTS
    # =====================================================

    from app.posts import posts_bp

    app.register_blueprint(posts_bp)

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    from app.notifications import notifications_bp

    app.register_blueprint(notifications_bp)

    # =====================================================
    # ADMIN
    # =====================================================

    from app.admin import admin_bp

    app.register_blueprint(admin_bp)

    # =====================================================
    # MESSAGES
    # =====================================================

    from app.messages import messages_bp

    app.register_blueprint(messages_bp)

    # =====================================================
    # MODÉRATION
    # =====================================================

    from app.moderation import moderation_bp

    app.register_blueprint(moderation_bp)

    # =====================================================
    # AUTORITÉ
    # =====================================================

    from app.authority import authority_bp

    app.register_blueprint(authority_bp)

    # =====================================================
    # CRÉATION AUTOMATIQUE DE L'ADMIN
    # =====================================================

    create_admin(app)

    return app