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

from .models import User

def create_app():
  app = Flask(__name__)

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