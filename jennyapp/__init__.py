from flask import Flask, url_for
# from flask_login import LoginManager

from .commands import create_tables
from .extensions import db, migrate, login_manager
from .routes import main
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
  app.register_blueprint(main)
  
  # COMMANDS
  app.cli.add_command(create_tables)

  return app