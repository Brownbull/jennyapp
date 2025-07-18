from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

from ..models import Session, Patient, User

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/dashboard')
@login_required
def index():
    from datetime import datetime, time
    now = datetime.now()
    # Get sessions for the logged-in medic
    all_sessions = Session.query.filter_by(doctor_email = current_user.email).all()
    incoming_sessions = []
    past_sessions = []
    for session in all_sessions:
        session_dt = datetime.combine(session.session_date, session.session_time)
        if session_dt > now:
            incoming_sessions.append(session)
        else:
            past_sessions.append(session)
    incoming_sessions.sort(key=lambda s: datetime.combine(s.session_date, s.session_time))
    past_sessions.sort(key=lambda s: datetime.combine(s.session_date, s.session_time), reverse=True)
    return render_template('dashboard/dashboard.html', incoming_sessions=incoming_sessions, past_sessions=past_sessions)

@dashboard_bp.route('/payments')
@login_required
def payments():
    sort = request.args.get('sort', 'desc')
    doctor = request.args.get('doctor', '')
    patient = request.args.get('patient', '')
    rut = request.args.get('rut', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    payment_status = request.args.get('payment_status', '')
    query = Session.query
    if doctor:
        query = query.filter(Session.doctor_email == doctor)
    if patient:
        query = query.filter(Session.patient_full_name == patient)
    if rut:
        # Join Patient to filter by rut_prefix
        query = query.join(Patient).filter(Patient.rut_prefix == rut)
    if payment_status:
        query = query.filter(Session.payment_status == payment_status)
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(Session.session_date >= from_date_obj)
        except Exception:
            pass
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(Session.session_date <= to_date_obj)
        except Exception:
            pass
    if sort == 'asc':
        query = query.order_by(Session.session_date.asc(), Session.session_time.asc())
    else:
        query = query.order_by(Session.session_date.desc(), Session.session_time.desc())
    sessions = query.all()

    # For filter dropdowns
    doctor_list = [u.email for u in User.query.all()]
    patient_list = [p.full_name for p in Patient.query.all()]
    rut_list = [str(p.rut_prefix) for p in Patient.query.filter(Patient.rut_prefix != None).distinct()]

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
    return render_template('dashboard/sessions/ses_payments.html', **context)