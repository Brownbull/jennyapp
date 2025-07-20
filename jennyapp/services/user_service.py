import io
from datetime import datetime
from flask import send_file, abort
from werkzeug.utils import secure_filename

from jennyapp.extensions import db
from jennyapp.models import User, UserProfile

def get_user_by_id_or_404(user_id):
    """Return a User object by its id.

    :param user_id: The id of the User to return.
    :return: The User with the given id.
    :raises 404: If no User with the given id exists.
    """
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    return user

def get_user_by_email(email):
    """Return the user with the given email address, or None if no user is found.

    :param email: email address to search for
    :return: user object or None
    """
    return User.query.filter_by(email=email).first()

def get_userprofile_by_user_id(user_id):
    """Return the UserProfile object for the given user_id, or create a new one if it doesn't exist.

    :param user_id: The ID of the user to retrieve the profile for.
    :return: The UserProfile object associated with the given user_id.
    """
    # First, attempt to retrieve the UserProfile object from the database
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()

    # If the UserProfile object doesn't exist, create a new one
    if not user_profile:
        # Create a new UserProfile object and associate it with the given user_id
        user_profile = UserProfile(user_id=user_id)

        # Retrieve the associated User object and assign its email to the UserProfile object
        user_profile.email = get_user_by_id_or_404(user_id).email

        db.session.add(user_profile)
        db.session.commit()

    return user_profile

def add_user(email, password):
    """Create a new user and add it to the database.

    :param email: The email address of the new user.
    :param password: The password for the new user.
    :return: The newly created User object.
    """
    new_user = User(email=email, password=password, join_date=datetime.now())

    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user_profile(user_profile, updated_user_data):
    """Update the UserProfile object with the given user data.

    This function takes a UserProfile object and a dictionary of updated user data as parameters, and updates the UserProfile object with the given data.

    :param user_profile: The UserProfile object to be updated.
    :param updated_user_data: A dictionary of the updated user data.
    :return: The updated UserProfile object.
    """
    # Loop through each key-value pair in the dictionary of updated user data
    for key, value in updated_user_data.items():
        # If the key is 'profile_picture', handle the profile picture upload
        if key == 'profile_picture':
            # Check if a profile picture was uploaded
            if value:
                # Get the file object from the request
                file = value
                # Get a secure filename for the uploaded file
                filename = secure_filename(file.filename)
                # Set
                user_profile.profile_picture_filename = filename
                user_profile.profile_picture = file.read()
        else:
            # For all other key-value pairs, set the attribute of the UserProfile object to the value
            setattr(user_profile, key, value)

    db.session.add(user_profile)
    db.session.commit()

    return user_profile

def get_user_profile_picture(user_id):
    """Return the profile picture of the user with the given user_id.

    :param user_id: The ID of the user whose profile picture is to be retrieved.
    :return: The profile picture of the user, or None if no picture exists.
    """
    profile = get_userprofile_by_user_id(user_id)
    if profile and profile.profile_picture:
        return send_file(io.BytesIO(profile.profile_picture), mimetype='image/jpeg')  # or detect mimetype
    else:
        # If no profile picture exists, return a 404 error
        return abort(404)

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

def del_user_profile(user_id):
    """Delete the user profile associated with the given user_id.

    :param user_id: The ID of the user whose profile is to be deleted.
    """
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if user_profile:
        db.session.delete(user_profile)
        db.session.commit()

def del_user(user):
    """Delete the given user and the associated user profile if it exists.

    This function takes a User object as a parameter, and deletes it from the database.
    Additionally, it deletes the associated UserProfile object if it exists.

    :param user: The User object to be deleted.
    """
    # Delete the associated UserProfile object if it exists
    del_user_profile(user.id)
    # Delete the user
    db.session.delete(user)
    db.session.commit()
