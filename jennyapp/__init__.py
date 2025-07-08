from flask import Flask

from .extensions import db, migrate, login_manager
from .models import User
from .utils import time_since
from .routes import main
from .commands import create_tables

def create_app(config_file='settings.py'):
  app = Flask(__name__)

  app.config.from_pyfile(config_file)

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