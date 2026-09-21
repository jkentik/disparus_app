from flask import Blueprint

authority_bp = Blueprint("authority", __name__, url_prefix="/authority")

from app.authority import routes