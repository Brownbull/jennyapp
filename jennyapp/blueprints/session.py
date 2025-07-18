from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from ..models import Patient, Session, User, SessionDocument
from ..extensions import db
from ..forms import SessionForm

session_bp = Blueprint('session', __name__, url_prefix='/session')

@session_bp.route('/')
@login_required
def index():
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

# Edit or add a session
@session_bp.route('/edit', methods=['GET', 'POST'])
@session_bp.route('/edit/<int:session_id>', methods=['GET', 'POST'])
@login_required
def edit(session_id=None):
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
            return redirect(url_for('session.index'))
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

@session_bp.route('/delete/<int:session_id>', methods=['GET', 'POST'])
@login_required
def delete(session_id):
    session = Session.query.get(session_id)
    if not session:
        from flask import flash
        flash(f'Session with id {session_id} not found or already deleted.', 'warning')
        return redirect(url_for('session.index', doctor=current_user.email))
    db.session.delete(session)
    db.session.commit()
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    # Redirect to sessions filtered by current user (doctor)
    return redirect(url_for('session.index', doctor=current_user.email))

