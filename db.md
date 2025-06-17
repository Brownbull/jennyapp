# init
$ flask shell
>>> from jennyapp import create_app
>>> from jennyapp.extensions import db
>>> from jennyapp.models import User, Patient, Session
>>> db.create_all()
>>> 