from flask_login import UserMixin
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    join_date = db.Column(db.Date, nullable=False, default=date.today())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
