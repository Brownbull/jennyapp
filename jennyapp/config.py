import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        # SQLite in instance folder by default
        f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'jennyapp.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF & session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    WTF_CSRF_ENABLED = True

    # Static cache busting
    STATIC_VERSION = os.environ.get("STATIC_VERSION", "1")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
