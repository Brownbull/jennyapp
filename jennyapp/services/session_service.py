from datetime import datetime

from jennyapp.models import Session, Patient
from jennyapp.extensions import db


def get_doctor_sessions(doctor_email):
    """
    Get all sessions for a given doctor.

    :param doctor_email: string representing doctor's email
    :return: list of Session objects
    """
    return Session.query.filter_by(doctor_email=doctor_email).all()


def is_incoming_session(session, now):
    """
    Check if a session is an incoming session.

    :param session: Session object
    :return: True if the session is incoming, False otherwise
    """
    # A session is considered incoming if its date is after today
    # Or if it's today but the session time is in the future
    return (session.session_date > now.date() or
            (session.session_date == now.date() and session.session_time > now.time()))

def get_inc_past_sessions(sessions):
    """
    Splits a list of sessions into incoming and past sessions.

    :param sessions: list of Session objects
    :return: tuple of two lists: incoming_sessions, past_sessions
    """
    # Get the current date and time
    now = datetime.now()
    
    # Initialize lists to store incoming and past sessions
    incoming_sessions = []
    past_sessions = []
    
    # Iterate through each session
    for session in sessions:
        if is_incoming_session(session, now): # Check if the session is incoming
            incoming_sessions.append(session)  # Add to incoming sessions
        else:
            past_sessions.append(session)  # Otherwise, add to past sessions
    
    # Return the lists of incoming and past sessions
    return incoming_sessions, past_sessions

def sort_sessions_by_datetime(sessions, reverse = False):
    """
    Sort a list of sessions by date and time.

    :param sessions: list of Session objects
    :param reverse: boolean indicating whether to sort in reverse order
    :return: sorted list of Session objects
    """
    sessions.sort(key=lambda s: (s.session_date, s.session_time), reverse=reverse)
    return sessions

def get_filtered_sessions(sort_order, doctor_email, patient_full_name, rut_prefix,
                          from_date_str, to_date_str, payment_status):
    """
    Get a list of sessions filtered by the given parameters.

    :param sort_order: string, either 'asc' or 'desc', indicating the order of the sessions
    :param doctor_email: string, doctor's email
    :param patient_full_name: string, patient's full name
    :param rut_prefix: string, RUT prefix
    :param from_date_str: string, starting date of the search in the format '%Y-%m-%d'
    :param to_date_str: string, ending date of the search in the format '%Y-%m-%d'
    :param payment_status: string, either 'paid' or 'unpaid', indicating the payment status
    :return: list of Session objects
    """
    query = Session.query
    
    if doctor_email:
        query = query.filter(Session.doctor_email == doctor_email)
    if patient_full_name:
        query = query.filter(Session.patient_full_name == patient_full_name)
    if rut_prefix:
        query = query.join(Patient).filter(Patient.rut_prefix == rut_prefix)
    if payment_status:
        query = query.filter(Session.payment_status == payment_status)
    
    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            query = query.filter(Session.session_date >= from_date)
        except ValueError:
            pass
    
    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            query = query.filter(Session.session_date <= to_date)
        except ValueError:
            pass
    
    if sort_order == 'asc':
        query = query.order_by(Session.session_date.asc(), Session.session_time.asc())
    else:
        query = query.order_by(Session.session_date.desc(), Session.session_time.desc())
    
    return query.all()
