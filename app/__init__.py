from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager
from app.models import User, Category, Post, Notification, Match, Country, Region, Message, Report

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User, Category, Post, Notification

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