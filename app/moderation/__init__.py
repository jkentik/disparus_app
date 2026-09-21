from flask import Blueprint

moderation_bp = Blueprint("moderation", __name__, url_prefix="/moderation")

from app.moderation import routes