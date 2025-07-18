from flask_login import login_user
from flask import redirect, url_for
from datetime import datetime

from jennyapp.extensions import db
from jennyapp.models import User

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def add_user(email, password):
    new_user = User(email=email, password=password, join_date=datetime.now())
    db.session.add(new_user)
    db.session.commit()
    return new_user

def user_email_exists(email):
    return get_user_by_email(email) is not None

def check_user_credentials(email, password):
    user = get_user_by_email(email)
    if user and user.verify_password(password):
        return user
    return None