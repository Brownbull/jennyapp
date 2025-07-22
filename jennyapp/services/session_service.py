from datetime import datetime
from flask import request
from flask_login import current_user
from werkzeug.utils import secure_filename

from jennyapp.forms import SessionForm
from jennyapp.models import Session, Patient, SessionDocument, User
from jennyapp.extensions import db

from jennyapp.services.user_service import get_user_by_email, get_users_email_list
from jennyapp.services.patient_service import get_patient_by_full_name, get_patient_by_id_or_404, get_patients_full_name_list, get_patients_rut_list, get_patient_name_by_id_or_404

def get_form():
    """
    Initialize the session form with the current user's email and the patient's name
    if the patient_id is provided in the request query string.

    Returns a tuple containing the session form, the existing documents, and the session object.
    """
    # Initialize the session form
    form = SessionForm()

    # Initialize the variables for the return tuple
    session_obj = None 
    existing_docs = []

    # Set the doctor's email in the form to the current user's email
    form.doctor_email.data = current_user.email

    # Get the patient_id from the request query string
    patient_id = request.args.get('patient_id')

    # If the patient_id is provided in the request query string, set the patient's full name
    if patient_id:
        form.patient_full_name.data = get_patient_name_by_id_or_404(patient_id)

    # Get the choices for the form fields
    get_choices(form)

    return form, existing_docs, session_obj

def get_form_by_id(session_id):
    """
    Initialize the session form with data from the session object identified by session_id.

    Parameters:
        session_id (int): The ID of the session to be edited.

    Returns a tuple containing the session form, the existing documents, and the session object.
    """
    # Get the session object from the database using the provided session_id
    session_obj = get_session_or_404(session_id)

    # Initialize the session form with the session object's data
    form = SessionForm(obj = session_obj)

    # Get the existing documents associated with the session
    existing_docs = get_session_documents(session_obj)

    # Set the doctor's email and the patient's full name in the form to the values from the session object
    form.doctor_email.data = session_obj.doctor_email
    form.patient_full_name.data = session_obj.patient_full_name

    # Get the choices for the form fields
    get_choices(form)

    return form, existing_docs, session_obj

def post_form(form, session_id=None):
    """
    Handles the POST request for the session form, either creating a new session or updating an existing one.

    Parameters:
        form (SessionForm): The session form containing the session data.
        session_id (int, optional): The ID of the session to be updated. Defaults to None.

    Returns:
        Session: The created or updated session object.
    """
    if session_id:
        # If a session_id is provided, retrieve the existing session object
        session_obj = get_session_or_404(session_id)
        # Update the existing session with the form data
        session_obj = update_session(session_obj, form)
    else:
        # If no session_id is provided, create a new session
        session_obj = add_session(form)

    # Handle document uploads and deletions
    handle_documents(session_obj, form, request.form.get('delete_ids', ''))

    return session_obj

def get_choices(form):
    """
    Initializes the session form with choices for doctor and patient fields.
    
    Parameters:
        form (SessionForm): The form to be initialized.
    """
    form.doctor_email.choices = get_users_email_list()
    form.patient_full_name.choices = get_patients_full_name_list()

    return form

def get_session_form_backrefs(form):    
    """
    Gets the user and patient objects based on the data in the given session form.

    Parameters:
        form (SessionForm): The session form containing the doctor's email and the patient's full name.

    Returns:
        tuple: A tuple containing the user object and the patient object.
    """
    user = get_user_by_email(form.doctor_email.data)
    patient = get_patient_by_full_name(form.patient_full_name.data)
        
    return user, patient

def add_session(form):
    """
    Adds a new session object to the database using the data from the given session form.

    Parameters:
        form (SessionForm): The session form containing the doctor's email, the patient's full name, and the session details.

    Returns:
        Session: The newly created session object.
    """
    user, patient = get_session_form_backrefs(form)
    print("Adding session for user:", user.email, "and patient:", patient.full_name)

    # Create a new session object
    session_obj = Session(
        # Backref fields
        user_id = user.id,
        patient_id = patient.id,
        # Form fields
        doctor_email = form.doctor_email.data,
        patient_full_name = form.patient_full_name.data,
        session_date = form.session_date.data,
        session_time = form.session_time.data,
        consent = form.consent.data,
        symptoms = form.symptoms.data,
        medications = form.medications.data,
        treatment = form.treatment.data,
        notes = form.notes.data,
        payment_method = form.payment_method.data,
        total_amount = form.total_amount.data,
        payment_status = form.payment_status.data
    )
    db.session.add(session_obj)
    db.session.commit()
    print("Session added successfully with ID:", session_obj.id)
    return session_obj

def update_session(session_obj, form):
    """
    Updates a session object with the given form data.

    :param session_obj: The session object to be updated.
    :param form: The form data containing the updated session information.

    Returns the updated session object.
    """
    user, patient = get_session_form_backrefs(form)
    
    # Update the session's other fields from the form data.
    # Backref fields
    session_obj.user_id = user.id
    session_obj.patient_id = patient.id
    # Form fields
    session_obj.doctor_email = form.doctor_email.data
    session_obj.patient_full_name = form.patient_full_name.data
    session_obj.session_date = form.session_date.data
    session_obj.session_time = form.session_time.data
    session_obj.consent = form.consent.data
    session_obj.symptoms = form.symptoms.data
    session_obj.medications = form.medications.data
    session_obj.treatment = form.treatment.data
    session_obj.notes = form.notes.data
    session_obj.payment_method = form.payment_method.data
    session_obj.total_amount = form.total_amount.data
    session_obj.payment_status = form.payment_status.data
    
    # Finally, commit the updated session to the database.
    db.session.commit()
    return session_obj

def handle_documents(session_obj, form, delete_ids):
    """
    Handle the deletion and uploading of session documents.

    :param session_obj: The session object to which the documents belong.
    :param form: The form data containing document files.
    :param delete_ids: A comma-separated string of document IDs to be deleted.
    
    This function deletes documents specified by `delete_ids` from the database 
    if they belong to the given session. It also uploads new documents from the form, 
    saving their binary data and metadata in the database.
    """
    # Check if there are any documents to delete
    if delete_ids:
        print("Deleting documents with IDs:", delete_ids)
        # Split the comma-separated string into individual document IDs
        for doc_id in delete_ids.split(','):
            # Remove any surrounding whitespace from the document ID
            doc_id = doc_id.strip()
            if doc_id:
                # Query the database to find the document by its ID
                doc = SessionDocument.query.get(int(doc_id))
                # Ensure the document belongs to the session before deleting
                if doc and doc.session_id == session_obj.id:
                    db.session.delete(doc)  # Mark the document for deletion
        # Commit the transaction to delete the marked documents
        db.session.commit()

    # Check if there are new documents to upload from the form
    if form.documents.data:
        print("Uploading new documents for session ID:", session_obj.id)
        # Iterate through each file in the form data
        for file in form.documents.data:
            # Ensure the file is not empty and has a filename
            if file and file.filename:
                # Secure the filename for safe storage
                filename = secure_filename(file.filename)
                # Read the file's binary content
                file_bytes = file.read()
                # Create a new SessionDocument object with metadata
                doc = SessionDocument(
                    session_id=session_obj.id,  # Associate with the session
                    filename=filename,          # Store the filename
                    file_data=file_bytes,       # Store the binary data
                    upload_date=datetime.now()  # Set the current upload date
                )
                db.session.add(doc)  # Add the new document to the session
        # Commit the transaction to save the uploaded documents
        db.session.commit()

def get_session_or_404(session_id):
    """Return a Session object by its id.

    :param session_id: The id of the Session to return.
    :return: The Session with the given id.
    :raises 404: If no Session with the given id exists.
    """
    return Session.query.get_or_404(session_id, description=f'Session with id {session_id} not found')

def get_session_documents(session_obj):
    """Get all documents associated with a session.

    :param session_obj: The Session object for which to retrieve documents.
    :return: A list of SessionDocument objects associated with the session.
    """
    return SessionDocument.query.filter_by(session_id=session_obj.id).all()

def get_doctor_sessions(doctor_email):
    """
    Get all sessions for a given doctor.

    :param doctor_email: string representing doctor's email
    :return: list of Session objects
    """
    return Session.query.filter_by(doctor_email=doctor_email).all()

def get_doctor_session_count_by_id(doctor_id):
    """
    Get the count of all sessions for a given doctor.

    :param doctor_id: integer representing doctor's ID
    :return: integer count of sessions
    """
    return Session.query.filter_by(user_id = doctor_id).count()

def get_patient_session_count(patient_id):
    """
    Get the count of all sessions for a given patient.

    :param patient_id: integer representing patient's ID
    :return: integer count of sessions
    """
    return Session.query.filter_by(patient_id=patient_id).count()

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
    Gets a list of sessions filtered by the given parameters.

    :param sort_order: string, either 'asc' or 'desc', indicating the order of the sessions
    :param doctor_email: string, doctor's email
    :param patient_full_name: string, patient's full name
    :param rut_prefix: string, RUT prefix
    :param from_date_str: string, starting date of the search in the format '%Y-%m-%d'
    :param to_date_str: string, ending date of the search in the format '%Y-%m-%d'
    :param payment_status: string, either 'paid' or 'unpaid', indicating the payment status
    :return: list of Session objects
    """
    # Start with the base query
    query = Session.query
    
    # Filter by doctor email if it is not empty
    if doctor_email:
        query = query.filter(Session.doctor_email == doctor_email)
    
    # Filter by patient full name if it is not empty
    if patient_full_name:
        query = query.filter(Session.patient_full_name == patient_full_name)
    
    # Filter by rut prefix if it is not empty
    # This involves joining the Patient table to compare the rut prefix
    if rut_prefix:
        query = query.join(Patient).filter(Patient.rut_prefix == rut_prefix)
    
    # Filter by payment status if it is not empty
    if payment_status:
        query = query.filter(Session.payment_status == payment_status)
    
    # Filter by date range if either the from date or to date is not empty
    if from_date_str or to_date_str:
        # Try to parse the dates
        try:
            if from_date_str:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                query = query.filter(Session.session_date >= from_date)
            if to_date_str:
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
                query = query.filter(Session.session_date <= to_date)
        except ValueError:
            # If the dates are not in the correct format, ignore the filters
            pass
    
    # Sort the sessions
    if sort_order == 'asc':
        query = query.order_by(Session.session_date.asc(), Session.session_time.asc())
    else:
        query = query.order_by(Session.session_date.desc(), Session.session_time.desc())
    
    # Finally, return the list of filtered sessions
    return query.all()

def get_sessions_context(request):
    """
    Get the context for the sessions page, including the filtered sessions and the values of the filters.

    :param request: Flask request object
    :return: dictionary with the context for the sessions page
    """

    # Get the sort order from the request query string
    sort_order = request.args.get('sort', 'desc')

    # Get the filter values from the request query string
    doctor_email = request.args.get('doctor', '')
    patient_full_name = request.args.get('patient', '')
    rut_prefix = request.args.get('rut', '')
    from_date_str = request.args.get('from_date', '')
    to_date_str = request.args.get('to_date', '')
    payment_status = request.args.get('payment_status', '')

    # Get the filtered sessions
    sessions = get_filtered_sessions(sort_order, doctor_email, patient_full_name, rut_prefix,
                                    from_date_str, to_date_str, payment_status)

    # Populate dropdown menus
    doctor_list = get_users_email_list()
    patient_list = get_patients_full_name_list()
    rut_list = get_patients_rut_list()

    # Create the context for the sessions page
    context = {
        'sessions': sessions,  # The filtered sessions
        'sort': sort_order,  # The sort order
        'doctor': doctor_email,  # The doctor filter
        'patient': patient_full_name,  # The patient filter
        'rut': rut_prefix,  # The RUT prefix filter
        'from_date': from_date_str,  # The from date filter
        'to_date': to_date_str,  # The to date filter
        'payment_status': payment_status,  # The payment status filter
        'doctor_list': doctor_list,  # The list of doctors to populate the dropdown menu
        'patient_list': patient_list,  # The list of patients to populate the dropdown menu
        'rut_list': rut_list,  # The list of RUT prefixes to populate the dropdown menu
    }

    return context

def del_sessions_by_patient_id(patient_id):
    """
    Deletes all sessions associated with a patient by their ID.

    :param patient_id: The ID of the patient whose sessions are to be deleted.
    """
    sessions = Session.query.filter_by(patient_id=patient_id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.commit()

def del_sessions_by_user_id(user_id):
    """
    Deletes all sessions associated with a user by their ID.

    :param user_id: The ID of the user whose sessions are to be deleted.
    """
    sessions = Session.query.filter_by(user_id=user_id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.commit()