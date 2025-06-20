from flask import Flask

from .extensions import db
from .views.main import main
def create_app(config_file='settings.py'):
  app = Flask(__name__)

  app.config.from_pyfile(config_file)

  db.init_app(app)

  app.register_blueprint(main)
  
  return app