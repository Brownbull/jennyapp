from datetime import datetime

from jennyapp.extensions import db
from jennyapp.models import User

def get_user_by_email(email):
    """Return the user with the given email address, or None if no user is found.

    :param email: email address to search for
    :return: user object or None
    """
    return User.query.filter_by(email=email).first()

def add_user(email, password):
    """
    Create a new user and add it to the database.

    :param email: The email address of the new user.
    :param password: The password for the new user.
    :return: The newly created User object.
    """
    new_user = User(email=email, password=password, join_date=datetime.now())
    db.session.add(new_user)
    db.session.commit()
    return new_user

def user_email_exists(email):
    """Return True if a user with the given email address exists, False otherwise.

    :param email: email address to search for
    :return: True if user exists, False otherwise
    """
    return get_user_by_email(email) is not None

def check_user_credentials(email, password):
    """Return the user object if the given email and password match an existing user, None if not.

    :param email: The email address to search for
    :param password: The password to check against
    :return: The matching User object if found, None otherwise
    """
    user = get_user_by_email(email)
    if user and user.verify_password(password):
        return user
    return None

def get_users_email_list():
    """Return a list of all users' emails."""
    return [user.email for user in User.query.all()]