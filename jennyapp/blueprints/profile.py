from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from jennyapp.services.user_service import get_userprofile_by_user_id, update_user_profile, get_user_profile_picture, get_user_by_id_or_404, del_user
from jennyapp.services.session_service import del_sessions_by_user_id, get_doctor_sessions

from ..forms import ProfileForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Handle GET and POST requests for the profile page.

    This function is responsible for rendering the profile page and
    processing the submission of the profile form.

    On GET requests, this function renders the profile template with the
    current user's information pre-filled in the form.

    On POST requests, this function validates the form data and updates the
    user's profile information in the database.

    :return: The rendered template for the profile page.
    """
    error = None

    # Get the user profile for the current user
    user_profile = get_userprofile_by_user_id(current_user.id)
    form = ProfileForm(obj=user_profile)

    if request.method == 'POST':
        # Validate the form data
        if form.validate_on_submit():
            # Create a dictionary of the updated user data
            updated_user_data = {
                'about': form.about.data,
                'full_name': form.full_name.data,
                'email': current_user.email,  # Email is not editable
                'phone_number_1': form.phone_number_1.data,
                'phone_number_2': form.phone_number_2.data,
                'address_1': form.address_1.data,
                'address_2': form.address_2.data,
                'city': form.city.data,
                'region': form.region.data,
                'country': form.country.data,
                'zip_code': form.zip_code.data,
                'notifications': form.notifications.data,
                'profile_picture': form.profile_picture.data
            }
            # Update the user's profile in the database
            update_user_profile(user_profile, updated_user_data)

            # Redirect the user to the profile page
            return redirect(url_for('profile.index'))
        
        
    # Calculate the session count for the current user
    session_count = len(get_doctor_sessions(current_user.id))

    # Create a context dictionary to pass to the template
    context = {
        'error': error,
        'form': form,
        'session_count': session_count
    }

    # Render the profile template with the context data
    return render_template('dashboard/profile.html', **context)

@profile_bp.route('/profile_image/<int:user_id>')
@login_required
def profile_image(user_id):
    """
    Return the profile picture for the user with the given user_id.

    :param user_id: The ID of the user whose profile picture is to be retrieved.
    :return: The profile picture of the user, or a 404 error if no picture exists.
    """
    return get_user_profile_picture(user_id)

@profile_bp.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete(user_id):
    """
    Deletes a user and all associated sessions from the database.

    This view function first retrieves the user by their ID. If the user
    exists, it deletes all sessions associated with the user and then deletes
    the user from the database. Finally, it redirects to the index page.

    :param user_id: The ID of the user to be deleted.
    :return: Redirect to the index page after successful deletion.
    """
    user = get_user_by_id_or_404(user_id)
    # Delete all sessions associated with this user (medic)
    del_sessions_by_user_id(user_id)
    # Delete the user
    del_user(user)
    return redirect(url_for('index.index'))