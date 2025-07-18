from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from ..extensions import db
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    sessions = db.relationship('Session', backref='user', lazy=True)
    user_profile = db.relationship('UserProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    about = db.Column(db.Text, default='')
    profile_picture_filename = db.Column(db.String(200), nullable=True)
    profile_picture = db.Column(db.LargeBinary, nullable=True)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone_number_1 = db.Column(db.String(20))
    phone_number_2 = db.Column(db.String(20))
    address_1 = db.Column(db.String(200))
    address_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    notifications = db.Column(db.Boolean, default=False)
    last_modification_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)