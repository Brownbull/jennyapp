from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from jennyapp.models import User, Patient
from jennyapp.extensions import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    errors = {}

    if request.method == 'POST':
        email = request.form.get('email')
        specialty = request.form.get('specialty')
        
        print(f"Received email: {email}, specialty: {specialty}")

        if not email:
            errors['email'] = 'Email is required'
        if not specialty:
            errors['specialty'] = 'Specialty is required'
        if not errors:
            print('No errors in input')
            user = User(
                email=email,
                specialty=specialty
            )
            db.session.add(user)
            db.session.commit()

            print('User added to database:', user)

            return redirect(url_for('main.index'))

    # Fetch all users from the database
    users = User.query.all()

    context = {
        'errors': errors,
        'users': users
    }
    return render_template('main.html', **context)

@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/user_panel/<int:user_id>', methods=['GET', 'POST'])
def user_panel(user_id):
    user = User.query.get_or_404(user_id)
    # Filtering and sorting
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'last_name')
    order = request.args.get('order', 'asc')
    query = Patient.query.filter_by(created_by=user.id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(like)) |
            (Patient.last_name.ilike(like)) |
            (Patient.rut.ilike(like)) |
            (Patient.email.ilike(like))
        )
    if sort in ['first_name', 'last_name', 'rut', 'email']:
        col = getattr(Patient, sort)
        if order == 'desc':
            col = col.desc()
        else:
            col = col.asc()
        query = query.order_by(col)
    patients = query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        specialty = request.form.get('specialty')
        user.email = email
        user.specialty = specialty
        db.session.commit()
        return redirect(url_for('main.user_panel', user_id=user.id))
    return render_template('user_panel.html', user=user, patients=patients, search=search, sort=sort, order=order)

@main.route('/user_panel/<int:user_id>/new_patient', methods=['GET', 'POST'])
def new_patient(user_id):
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob  = datetime.strptime(request.form.get('dob'), '%Y-%m-%d') if request.form.get('dob') else None
        email = request.form.get('email')
        phone = request.form.get('phone')
        rut = request.form.get('rut')
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=email,
            phone=phone,
            rut=rut,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('main.user_panel', user_id=user_id))
    return render_template('new_patient.html', user_id=user_id)

@main.route('/user_panel/<int:user_id>/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(user_id, patient_id):
    from jennyapp.models import Patient
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('main.user_panel', user_id=user_id))

@main.route('/user_panel/<int:user_id>/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(user_id, patient_id):
    from jennyapp.models import Patient
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        if dob:
            from datetime import datetime
            patient.dob = datetime.strptime(dob, '%Y-%m-%d')
        patient.email = request.form.get('email')
        patient.phone = request.form.get('phone')
        patient.rut = request.form.get('rut')
        db.session.commit()
        return redirect(url_for('main.user_panel', user_id=user_id))
    return render_template('edit_patient.html', patient=patient, user_id=user_id)

@main.route('/user_panel/<int:user_id>/new_session/<int:patient_id>', methods=['GET', 'POST'])
def new_session(user_id, patient_id):
    from jennyapp.models import Session
    from datetime import datetime
    if request.method == 'POST':
        date_str = request.form.get('date')
        notes = request.form.get('notes')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else None
        session = Session(user_id=user_id, patient_id=patient_id, date=date, notes=notes)
        db.session.add(session)
        db.session.commit()
        return redirect(url_for('main.user_panel', user_id=user_id))
    return render_template('new_session.html', user_id=user_id)

@main.route('/user_panel/<int:user_id>/patient_sessions/<int:patient_id>')
def patient_sessions(user_id, patient_id):
    from jennyapp.models import Patient, Session
    patient = Patient.query.get_or_404(patient_id)
    sessions = [s for s in patient.sessions if s.user_id == user_id]
    return render_template('patient_sessions.html', patient=patient, sessions=sessions, user_id=user_id)

@main.route('/user_panel/<int:user_id>/delete_session/<int:session_id>/<int:patient_id>', methods=['POST'])
def delete_session(user_id, session_id, patient_id):
    from jennyapp.models import Session
    session = Session.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return redirect(url_for('main.patient_sessions', user_id=user_id, patient_id=patient_id))

@main.route('/user_panel/<int:user_id>/edit_session/<int:session_id>/<int:patient_id>', methods=['GET', 'POST'])
def edit_session(user_id, session_id, patient_id):
    from jennyapp.models import Session
    from datetime import datetime
    session = Session.query.get_or_404(session_id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        notes = request.form.get('notes')
        if date_str:
            session.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        session.notes = notes
        db.session.commit()
        return redirect(url_for('main.patient_sessions', user_id=user_id, patient_id=patient_id))
    return render_template('edit_session.html', session=session, user_id=user_id, patient_id=patient_id)