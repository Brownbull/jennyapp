import os

from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from jennyapp.services.user_service import get_userprofile_by_user_id
from jennyapp.services.session_service import get_doctor_session_count_by_id

from ..models import User, Session, UserProfile
from ..extensions import db
from ..forms import ProfileForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    form = ProfileForm()

    # Get the user profile for the current user
    user_profile = get_userprofile_by_user_id(current_user.id)

    # Calculate session count for current user
    session_count = get_doctor_session_count_by_id(current_user.id)

    if request.method == 'POST': # HEREEEEEEEEEEEE!
        if form.validate_on_submit():
            user_profile.about = form.about.data
            user_profile.full_name = form.full_name.data
            user_profile.email = current_user.email  # Email is not editable
            user_profile.phone_number_1 = form.phone_number_1.data
            user_profile.phone_number_2 = form.phone_number_2.data
            user_profile.address_1 = form.address_1.data
            user_profile.address_2 = form.address_2.data
            user_profile.city = form.city.data
            user_profile.region = form.region.data
            user_profile.country = form.country.data
            user_profile.zip_code = form.zip_code.data
            user_profile.notifications = form.notifications.data
            # Handle profile picture upload
            if form.profile_picture.data:
                file = form.profile_picture.data
                filename = secure_filename(file.filename)
                user_profile.profile_picture_filename = filename
                user_profile.profile_picture = file.read()
            db.session.commit()
            return redirect(url_for('profile.index'))
    else:
        # Pre-fill form with existing profile data
        if user_profile:
            form.about.data = user_profile.about
            form.full_name.data = user_profile.full_name
            form.email.data = current_user.email
            form.phone_number_1.data = user_profile.phone_number_1
            form.phone_number_2.data = user_profile.phone_number_2
            form.address_1.data = user_profile.address_1
            form.address_2.data = user_profile.address_2
            form.city.data = user_profile.city
            form.region.data = user_profile.region
            form.country.data = user_profile.country
            form.zip_code.data = user_profile.zip_code
            form.notifications.data = user_profile.notifications
            form.profile_picture.data = user_profile.profile_picture_filename
        else:
            form.email.data = current_user.email
    return render_template('dashboard/profile.html', form=form, session_count=session_count)

@profile_bp.route('/profile_image/<int:user_id>')
@login_required
def profile_image(user_id):
    from ..models import UserProfile
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile and profile.profile_picture:
        from flask import send_file
        import io
        return send_file(io.BytesIO(profile.profile_picture), mimetype='image/jpeg')  # or detect mimetype
    abort(404)

@profile_bp.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete(user_id):
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    # Delete all sessions associated with this user (medic)
    sessions = Session.query.filter_by(user_id=user.id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index.index'))