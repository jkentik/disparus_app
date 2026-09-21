import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-me-en-prod"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get("postgresql://disparus_db_user:IfhDhABebPqt66ZO53XMWla3UyV9MAYZ@dpg-dao0s60ae00c73aca2a0-a/disparus_db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "app",
        "static",
        "uploads"
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo par fichier


















