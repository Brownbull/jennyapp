from flask import Flask, url_for
import os
# from flask_login import LoginManager

from .commands import create_tables
from .extensions import db, migrate, login_manager
# from .routes import main
from .blueprints.index import index_bp
from .blueprints.auth import auth_bp
from .blueprints.profile import profile_bp
from .blueprints.patient import patient_bp
from .blueprints.session import session_bp
from .blueprints.dashboard import dashboard_bp
from .utils import time_since
from .config import DevelopmentConfig, ProductionConfig

from .models import User

def create_app():
  app = Flask(__name__)

  # Load configuration: prefer FLASK_ENV=production to switch
  env = os.environ.get("FLASK_ENV", "development").lower()
  if env == "production":
    app.config.from_object(ProductionConfig)
  else:
    app.config.from_object(DevelopmentConfig)

  # Allow overrides via environment prefix (FLASK_*)
  app.config.from_prefixed_env()

  db.init_app(app)
  migrate.init_app(app, db)
  login_manager.init_app(app)

  login_manager.login_view = 'main.index'

  @login_manager.user_loader
  def load_user(user_id):
      return User.query.get(user_id)

  # UTILS
  app.add_template_filter(time_since, 'time_since')

  # Jinja helper to cache-bust static assets with STATIC_VERSION
  @app.context_processor
  def inject_static_version():
    return {"static_v": app.config.get("STATIC_VERSION", "1")}

  # Basic error pages
  @app.errorhandler(404)
  def _404(e):
    return (app.jinja_env.get_or_select_template(["errors/404.html"]).render(), 404)

  @app.errorhandler(500)
  def _500(e):
    return (app.jinja_env.get_or_select_template(["errors/500.html"]).render(), 500)

  # ROUTES
  # app.register_blueprint(main)
  app.register_blueprint(index_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(profile_bp)
  app.register_blueprint(patient_bp)
  app.register_blueprint(session_bp)
  app.register_blueprint(dashboard_bp)
  
  # COMMANDS
  app.cli.add_command(create_tables)

  return app