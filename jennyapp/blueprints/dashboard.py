from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from ..services.session_service import get_doctor_sessions, get_inc_past_sessions, sort_sessions_by_datetime, get_sessions_context

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    The main dashboard view for medics. Shows incoming and past sessions.

    :returns: A rendered template of the dashboard.
    """
    incoming_sessions = []
    past_sessions = []
    
    # Get sessions for the logged-in medic
    all_sessions = get_doctor_sessions(current_user.email)

    if all_sessions:
        # Get incoming and past sessions
        incoming_sessions, past_sessions = get_inc_past_sessions(all_sessions)

        # Sort sessions
        incoming_sessions = sort_sessions_by_datetime(incoming_sessions)
        past_sessions = sort_sessions_by_datetime(past_sessions, reverse=True)

    context = {
        'incoming_sessions': incoming_sessions,
        'past_sessions': past_sessions,
    }

    return render_template('dashboard/dashboard.html', **context)

@dashboard_bp.route('/payments')
@login_required
def payments():
    context = get_sessions_context(request)
    return render_template('dashboard/sessions/ses_payments.html', **context)
