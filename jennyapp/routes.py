
from flask import Blueprint, render_template, url_for, redirect, request, current_app, abort
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
UPLOAD_FOLDER = 'static/uploads'

from .extensions import db
from .forms import RegisterForm, LoginForm, PatientForm, SessionForm, ProfileForm
from .models import User, Patient, Session, SessionDocument

main = Blueprint('main', __name__)
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            error = "Email address already exists. Please use a different email."
        else:
            register_user = User(
                email=form.email.data,
                password=form.password.data,
                join_date=datetime.now()
            )
            db.session.add(register_user)
            db.session.commit()
            login_user(register_user, remember=False) 
            return redirect(url_for('main.dashboard'))
        
    context = {
        'form': form,
        'error': error
    }
    return render_template('register.html', **context)

@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.verify_password(form.password.data):
            error = 'Invalid username or password'
        else:
            login_user(user, remember=form.remember_me.data) 
            return redirect(url_for('main.dashboard'))

    context = {
        'form': form,
        'error': error,
    }
    return render_template('login.html', **context)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime, time
    now = datetime.now()
    # Get sessions for the logged-in medic
    all_sessions = Session.query.filter_by(doctor_email=current_user.email).all()
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

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from .forms import ProfileForm
    from .models import UserProfile
    from werkzeug.utils import secure_filename
    import os
    form = ProfileForm()
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST' and form.validate_on_submit():
        if not user_profile:
            user_profile = UserProfile(user_id=current_user.id)
            db.session.add(user_profile)
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
        return redirect(url_for('main.profile'))
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
    return render_template('dashboard/profile.html', form=form)

@main.route('/profile_image/<int:user_id>')
@login_required
def profile_image(user_id):
    from .models import UserProfile
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile and profile.profile_picture:
        from flask import send_file
        import io
        return send_file(io.BytesIO(profile.profile_picture), mimetype='image/jpeg')  # or detect mimetype
    abort(404)

@main.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    # Delete all sessions associated with this user (medic)
    sessions = Session.query.filter_by(user_id=user.id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/patients')
@login_required
def patients():
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

@main.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
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
        
        return redirect(url_for('main.patients'))
    
    context = {
        'form': form,
        'error': error
    }
    return render_template('dashboard/patients/pat_add.html', **context)

@main.route('/', methods=['GET', 'POST'], defaults = {'patient_id': None})
@main.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
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
        return redirect(url_for('main.patients'))

    context = {
        'form': form,
        'error': error,
        'patient_id': patient_id,
        'edit_patient': edit_patient
    }
    
    return render_template('dashboard/patients/pat_edit.html', **context)

@main.route('/delete_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id, description=f'Patient with id {patient_id} not found')
    # Delete all sessions associated with this patient using ORM
    from .models import Session
    sessions = Session.query.filter_by(patient_id=patient.id).all()
    for session in sessions:
        db.session.delete(session)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('main.patients'))

@main.route('/sessions')
@login_required
def sessions():
    sort = request.args.get('sort', 'desc')
    doctor = request.args.get('doctor', '')
    patient = request.args.get('patient', '')
    rut = request.args.get('rut', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    query = Session.query
    if doctor:
        query = query.filter(Session.doctor_email == doctor)
    if patient:
        query = query.filter(Session.patient_full_name == patient)
    if rut:
        # Join Patient to filter by rut_prefix
        query = query.join(Patient).filter(Patient.rut_prefix == rut)
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
        'doctor_list': doctor_list,
        'patient_list': patient_list,
        'rut_list': rut_list,
    }
    return render_template('dashboard/sessions/ses_index.html', **context)

@main.route('/payments')
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


# Edit or add a session
@main.route('/edit_session', methods=['GET', 'POST'])
@main.route('/edit_session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def edit_session(session_id=None):
    error = None
    session_obj = None
    doctor_choices = [(u.email, u.email) for u in User.query.all()]
    patient_choices = [(p.full_name, p.full_name) for p in Patient.query.all()]
    existing_docs = []

    if session_id:
        session_obj = Session.query.get_or_404(session_id, description=f'Session with id {session_id} not found')
        form = SessionForm(obj=session_obj)
        form.doctor_email.choices = doctor_choices
        form.patient_full_name.choices = patient_choices
        existing_docs = SessionDocument.query.filter_by(session_id=session_obj.id).all()
        if request.method == 'GET':
            form.doctor_email.data = session_obj.doctor_email
            form.patient_full_name.data = session_obj.patient_full_name

    else:
        form = SessionForm()
        form.doctor_email.choices = doctor_choices
        form.patient_full_name.choices = patient_choices
        existing_docs = []
        # Set default doctor to current user
        if not form.doctor_email.data:
            form.doctor_email.data = current_user.email
        # Preselect patient if patient_id is provided in query string
        patient_id = request.args.get('patient_id')
        if patient_id:
            patient = Patient.query.get(int(patient_id))
            if patient:
                form.patient_full_name.data = patient.full_name

    if request.method == 'POST':
        if form.validate_on_submit():
            if session_obj:
                # Update existing session
                session_obj.doctor_email = form.doctor_email.data
                user = User.query.filter_by(email=form.doctor_email.data).first()
                if user:
                    session_obj.user_id = user.id
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
                db.session.commit()
                # Handle document deletions
                delete_ids = request.form.get('delete_documents', '')
                if delete_ids:
                    for doc_id in delete_ids.split(','):
                        doc_id = doc_id.strip()
                        if doc_id:
                            doc = SessionDocument.query.get(int(doc_id))
                            if doc and doc.session_id == session_obj.id:
                                db.session.delete(doc)
                    db.session.commit()
                # Handle file uploads for update (store only in DB)
                if form.documents.data:
                    for file in form.documents.data:
                        if file and file.filename:
                            filename = secure_filename(file.filename)
                            file_bytes = file.read()
                            doc = SessionDocument(
                                session_id=session_obj.id,
                                filename=filename,
                                file_data=file_bytes,
                                upload_date=datetime.now()
                            )
                            db.session.add(doc)
                    db.session.commit()
            else:
                # Create new session
                patient = Patient.query.filter_by(full_name=form.patient_full_name.data).first()
                if not patient:
                    patient = Patient(full_name=form.patient_full_name.data)
                    db.session.add(patient)
                    db.session.commit()
                # Always use current_user for new session
                session_obj = Session(
                    user_id=current_user.id,
                    patient_id=patient.id,
                    doctor_email=current_user.email,
                    patient_full_name=form.patient_full_name.data,
                    session_date=form.session_date.data,
                    session_time=form.session_time.data,
                    consent=form.consent.data,
                    symptoms=form.symptoms.data,
                    medications=form.medications.data,
                    treatment=form.treatment.data,
                    notes=form.notes.data,
                    payment_method=form.payment_method.data,
                    total_amount=form.total_amount.data,
                    payment_status=form.payment_status.data
                )
                db.session.add(session_obj)
                db.session.commit()
                # Handle file uploads for new session (store only in DB)
                if form.documents.data:
                    for file in form.documents.data:
                        if file and file.filename:
                            filename = secure_filename(file.filename)
                            file_bytes = file.read()
                            doc = SessionDocument(
                                session_id=session_obj.id,
                                filename=filename,
                                file_data=file_bytes,
                                upload_date=datetime.now()
                            )
                            db.session.add(doc)
                    db.session.commit()
            return redirect(url_for('main.sessions'))
        else:
            error = 'Form validation failed. Please check your input.'

    context = {
        'error': error,
        'form': form,
        'session_id': session_id,
        'session_obj': session_obj,
        'existing_docs': existing_docs
    }
    return render_template('dashboard/sessions/ses_edit.html', **context)

@main.route('/delete_session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def delete_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        from flask import flash
        flash(f'Session with id {session_id} not found or already deleted.', 'warning')
        return redirect(url_for('main.sessions', doctor=current_user.email))
    db.session.delete(session)
    db.session.commit()
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    # Redirect to sessions filtered by current user (doctor)
    return redirect(url_for('main.sessions', doctor=current_user.email))

