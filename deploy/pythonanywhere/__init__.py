from flask import Flask, url_for
import os
# from flask_login import LoginManager

from .commands import create_tables
from .extensions import db, migrate, login_manager
from .routes import main
from .utils import time_since

from .models import User

def create_app():
  app = Flask(__name__)

  app.config.from_prefixed_env()

  app.config['SECRET_KEY'] = '928236543'
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/brownbull/jennyapp/instance/jennyapp.db'

  db_uri = os.environ.get('JENNYAPP_DB_URI')
  if db_uri:
      app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
  else:
      # Default to local SQLite
      app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/jennyapp.db'

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