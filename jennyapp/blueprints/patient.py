from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import datetime

from jennyapp.services.patient_service import get_patients, add_patient, get_patient_by_id_or_404, edit_patient, del_patient
from jennyapp.services.session_service import get_patient_sessions, del_sessions_by_patient_id

from ..forms import PatientForm

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/')
@login_required
def index():
    """
    Render the patient index page.

    This view function retrieves all patients from the database and calculates
    the session count for each patient. It then prepares a context dictionary
    with the patient data, which includes both the patient information and their
    session counts. The patient index template is rendered with this context
    data.

    :return: Rendered template for the patient index page displaying patients
             and their session counts.
    """
    # Retrieve all patients from the database using the patient service
    patients = get_patients()

    # Initialize an empty list to store patient data including session counts
    patient_data = []

    # Check if there are any patients retrieved
    if patients:
        for patient in patients:
            # Get the count of sessions for the current patient
            session_count = len(get_patient_sessions(patient.id))
            
            # Append a dictionary containing the patient object and session count to the patient_data list
            patient_data.append({
                'patient': patient,
                'session_count': session_count
            })

    context = {
        'patients': patient_data  # The list of patients with their session counts
    }

    return render_template('dashboard/patients/pat_index.html', **context)

@patient_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Handles the addition of a new patient.

    This view function is responsible for rendering the patient addition form
    and handling the addition of a new patient. When the form is submitted,
    the submitted form data is validated. If the form is valid, the data is
    stored in a dictionary and used to create a new patient object using the
    add_patient service. The new patient object is then added to the database
    and the user is redirected to the patient index page.

    :return: Rendered template for the patient addition form or redirect to the
             patient index page if the form is valid.
    """
    error = None
    form = PatientForm()
    
    # Get the current date
    current_date = datetime.now() 

    if form.validate_on_submit():
        # Collect patient data from the form fields
        patient_data = {
            'full_name': form.full_name.data,
            'occupation': form.occupation.data,
            'rut_prefix': form.rut_prefix.data,
            'rut_suffix': form.rut_suffix.data,
            'date_of_birth': form.date_of_birth.data,
            'gender' : form.gender.data,
            'email' : form.email.data,
            'phone_number_1' : form.phone_number_1.data,
            'phone_number_2' : form.phone_number_2.data,
            'address_1' : form.address_1.data,
            'address_2' : form.address_2.data,
            'city' : form.city.data,
            'region' : form.region.data,
            'country' : form.country.data,
            'zip_code' : form.zip_code.data,
            'notifications' : form.notifications.data,
            'join_date' : current_date,
            'medical_history' : "",
            'current_medications' : "",
            'allergies' : "",
            'emergency_contact_name' : "",
            'emergency_contact_number' : "",
            'emergency_contact_relationship' : "",
        }
        
        # Add the new patient using the service
        new_patient = add_patient(patient_data)

        return redirect(url_for('patient.index'))
    
    context = {
        'form': form,
        'error': error
    }
    return render_template('dashboard/patients/pat_add.html', **context)

@patient_bp.route('/', methods=['GET', 'POST'], defaults={'patient_id': None})
@patient_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit(patient_id):
    """
    Handles the editing of a patient's information. If a patient ID is provided,
    retrieves the patient's details and populates the form with them. On form 
    submission, updates the patient's information with the provided data.

    Routes:
        - GET '/': Display a form to edit patient if patient_id is provided.
        - POST '/': Submit form data to update an existing patient.
        - GET '/edit/<int:patient_id>': Display a form to edit specific patient.
        - POST '/edit/<int:patient_id>': Submit form data to update specific patient.

    Parameters:
        patient_id (int, optional): The ID of the patient to be edited. Defaults to None.

    Returns:
        Redirect to patient index page upon successful update, or re-renders the 
        edit form with error messages if any issues occur during the process.
    """
    error = {}
    form = PatientForm()
    patient = None

    # If a patient ID is provided, retrieve patient details
    if patient_id:
        # Retrieve the patient object by ID, or return a 404 error if not found
        patient = get_patient_by_id_or_404(patient_id)
        # Pre-populate the form with the patient's existing data
        form = PatientForm(obj=patient)

    if request.method == 'POST':
        # If a patient object exists, update it with the form data
        if patient:
            # Collect updated patient data from the form fields
            updated_patient_data = {
                'full_name': request.form['full_name'],
                'occupation': request.form['occupation'],
                'rut_prefix': request.form['rut_prefix'],
                'rut_suffix': request.form['rut_suffix'],
                'date_of_birth': request.form['date_of_birth'],
                'gender': request.form['gender'],
                'email': request.form['email'],
                'phone_number_1': request.form['phone_number_1'],
                'phone_number_2': request.form['phone_number_2'],
                'address_1': request.form['address_1'],
                'address_2': request.form['address_2'],
                'city': request.form['city'],
                'region': request.form['region'],
                'country': request.form['country'],
                'zip_code': request.form['zip_code'],
                'notifications': True if request.form['notifications'] == 'y' else False,
                'medical_history': request.form['medical_history'],
                'current_medications': request.form['current_medications'],
                'allergies': request.form['allergies'],
                'emergency_contact_name': request.form['emergency_contact_name'],
                'emergency_contact_number': request.form['emergency_contact_number'],
                'emergency_contact_relationship': request.form['emergency_contact_relationship'],
                'deceased': True if request.form['deceased'] == 'y' else False
            }
            # Update the patient object with the new data
            patient = edit_patient(patient, updated_patient_data)
        # Redirect to the patient index page after updating
        return redirect(url_for('patient.index'))

    # Prepare the context for rendering the edit form template
    context = {
        'form': form,
        'error': error,
        'patient_id': patient_id,
        'patient_edited': patient
    }

    # Render the edit form template with the context data
    return render_template('dashboard/patients/pat_edit.html', **context)

@patient_bp.route('/delete/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def delete(patient_id):
    """
    Deletes a patient and all associated sessions from the database.

    This view function first retrieves the patient by their ID. If the patient
    exists, it deletes all sessions associated with the patient and then deletes
    the patient from the database. Finally, it redirects to the patient index page.

    :param patient_id: The ID of the patient to be deleted.
    :return: Redirect to the patient index page after successful deletion.
    """
    patient = get_patient_by_id_or_404(patient_id)
    if patient:
        # Delete all sessions associated with this patient
        del_sessions_by_patient_id(patient_id)
        # Delete the patient
        del_patient(patient)
    return redirect(url_for('patient.index'))