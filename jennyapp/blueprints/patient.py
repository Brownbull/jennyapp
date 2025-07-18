from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import datetime

from ..models import Patient, Session
from ..extensions import db
from ..forms import PatientForm

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/')
@login_required
def index():
    patients = Patient.query.all()
    # Build a list of dicts with patient and session_count
    patient_data = []
    for patient in patients:
        session_count = Session.query.filter_by(patient_id=patient.id).count()
        patient_data.append({
            'patient': patient,
            'session_count': session_count
        })
    return render_template('dashboard/patients/pat_index.html', patients=patient_data)

@patient_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    error = None
    form = PatientForm()
    current_date = datetime.now() 

    if form.validate_on_submit():
        new_patient = Patient(
            full_name = form.full_name.data,
            occupation = form.occupation.data,
            rut_prefix = form.rut_prefix.data,
            rut_suffix = form.rut_suffix.data,
            # date_of_birth = datetime.strptime(form.date_of_birth.data, '%Y-%m-%d').date(),
            date_of_birth=form.date_of_birth.data,
            gender = form.gender.data,
            email = form.email.data,
            phone_number_1 = form.phone_number_1.data,
            phone_number_2 = form.phone_number_2.data,
            address_1 = form.address_1.data,
            address_2 = form.address_2.data,
            city = form.city.data,
            region = form.region.data,
            country = form.country.data,
            zip_code = form.zip_code.data,
            notifications = form.notifications.data,
            join_date = current_date,
            # ME
            medical_history = "",
            current_medications = "",
            allergies = "",
            emergency_contact_name = "",
            emergency_contact_number = "",
            emergency_contact_relationship = "",
            )
        
        db.session.add(new_patient)
        db.session.commit()
        
        return redirect(url_for('patient.index'))
    
    context = {
        'form': form,
        'error': error
    }
    return render_template('dashboard/patients/pat_add.html', **context)

@patient_bp.route('/', methods=['GET', 'POST'], defaults = {'patient_id': None})
@patient_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit(patient_id):
    edit_patient = None
    error = {}
    form = PatientForm()

    if patient_id:
        edit_patient = Patient.query.get_or_404(patient_id, description=f'Patient with id {patient_id} not found')
        form = PatientForm(obj=edit_patient)
    else:
        form = PatientForm()
        # print(f"date_of_birth: {edit_patient.date_of_birth} {type({edit_patient.date_of_birth})}")

    if request.method == 'POST':
        print(request.form['notifications'])
        edit_patient.full_name = request.form['full_name']
        edit_patient.occupation = request.form['occupation']
        edit_patient.rut_prefix = request.form['rut_prefix']
        edit_patient.rut_suffix = request.form['rut_suffix']
        edit_patient.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        edit_patient.gender = request.form['gender']
        edit_patient.email = request.form['email']
        edit_patient.phone_number_1 = request.form['phone_number_1']
        edit_patient.phone_number_2 = request.form['phone_number_2']
        edit_patient.address_1 = request.form['address_1']
        edit_patient.address_2 = request.form['address_2']
        edit_patient.city = request.form['city']
        edit_patient.region = request.form['region']
        edit_patient.country = request.form['country']
        edit_patient.zip_code = request.form['zip_code']
        edit_patient.notifications = True if request.form['notifications']  == 'y' else False
        edit_patient.medical_history = request.form['medical_history']
        edit_patient.current_medications = request.form['current_medications']
        edit_patient.allergies = request.form['allergies']
        edit_patient.emergency_contact_name = request.form['emergency_contact_name']
        edit_patient.emergency_contact_number = request.form['emergency_contact_number']
        edit_patient.emergency_contact_relationship = request.form['emergency_contact_relationship']
        edit_patient.deceased = True if request.form['notifications']  == 'y' else False
        db.session.commit()
        print("Patient updated")
        return redirect(url_for('patient.index'))

    context = {
        'form': form,
        'error': error,
        'patient_id': patient_id,
        'edit_patient': edit_patient
    }
    
    return render_template('dashboard/patients/pat_edit.html', **context)

@patient_bp.route('/delete/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def delete(patient_id):
    patient = Patient.query.get_or_404(patient_id, description=f'Patient with id {patient_id} not found')
    # Delete all sessions associated with this patient using ORM
    from ..models import Session
    sessions = Session.query.filter_by(patient_id=patient.id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patient.index'))