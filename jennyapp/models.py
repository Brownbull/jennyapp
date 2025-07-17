from datetime import datetime
from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    sessions = db.relationship('Session', backref='user', lazy=True)
    user_profile = db.relationship('UserProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    about = db.Column(db.Text, default='')
    profile_picture_filename = db.Column(db.String(200), nullable=True)
    profile_picture = db.Column(db.LargeBinary, nullable=True)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone_number_1 = db.Column(db.String(20))
    phone_number_2 = db.Column(db.String(20))
    address_1 = db.Column(db.String(200))
    address_2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    notifications = db.Column(db.Boolean, default=False)
    last_modification_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    rut_prefix = db.Column(db.Integer)
    rut_suffix = db.Column(db.String(1))
    full_name = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone_number_1 = db.Column(db.String(20), nullable=True)
    phone_number_2 = db.Column(db.String(20), nullable=True)
    address_1 = db.Column(db.String(200), nullable=True)
    address_2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    notifications = db.Column(db.Boolean, nullable=True)
    join_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    # MEDICAL
    medical_history = db.Column(db.String(200), nullable=True)
    current_medications = db.Column(db.String(200), nullable=True)
    allergies = db.Column(db.String(200), nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_number = db.Column(db.String(20), nullable=True)
    emergency_contact_relationship = db.Column(db.String(100), nullable=True)

    sessions = db.relationship('Session', backref='patient', lazy=True)

# Session model for appointments
class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_email = db.Column(db.String(120), nullable=False)
    patient_full_name = db.Column(db.String(200), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    consent = db.Column(db.Boolean, nullable=True)
    reason_for_visit = db.Column(db.String(200), nullable=False)
    medications = db.Column(db.String(200), nullable=True)
    diagnostic = db.Column(db.String(200), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Integer, nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default='unpaid')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    documents = db.relationship('SessionDocument', backref='session', cascade="all, delete-orphan")

class SessionDocument(db.Model):
    __tablename__ = 'session_documents'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete="CASCADE"), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    
