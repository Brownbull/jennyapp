from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from ..services.user_service import get_users_email_list
from ..services.patient_service import get_patients_full_name_list, get_patients_rut_list
from ..services.session_service import get_doctor_sessions, get_inc_past_sessions, sort_sessions_by_datetime, get_filtered_sessions

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
    """
    The payments view for medics. Shows all past sessions with payments.

    The sessions are filtered by the following parameters:

    :param sort: The sort order, either 'asc' or 'desc'.
    :param doctor: The email of the doctor to filter sessions by.
    :param patient: The full name of the patient to filter sessions by.
    :param rut: The rut of the patient to filter sessions by.
    :param from_date: The date to filter sessions from.
    :param to_date: The date to filter sessions to.
    :param payment_status: The payment status to filter sessions by, either 'paid' or 'unpaid'.

    :returns: A rendered template of the payments page.
    """
    # Get the field from the url parameters.
    # If it's not present, then use default.
    sort = request.args.get('sort', 'desc')
    doctor = request.args.get('doctor', '')
    patient = request.args.get('patient', '')
    rut = request.args.get('rut', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    payment_status = request.args.get('payment_status', '')

    # Get the filtered sessions based on the parameters above.
    sessions = get_filtered_sessions(sort, doctor, patient, rut, from_date, to_date, payment_status)

    # Get the lists of doctors, patients, and ruts for the filter dropdowns.
    doctor_list = get_users_email_list()
    patient_list = get_patients_full_name_list()
    rut_list = get_patients_rut_list()

    # Create a context dictionary with the sessions and the filter parameters.
    context = {
        'sessions': sessions,
        'sort': sort,
        'doctor': doctor,
        'patient': patient,
        'rut': rut,
        'from_date': from_date,
        'to_date': to_date,
        'payment_status': payment_status,
        'doctor_list': doctor_list,
        'patient_list': patient_list,
        'rut_list': rut_list,
    }

    # Render the payments template with the context dictionary.
    return render_template('dashboard/sessions/ses_payments.html', **context)
