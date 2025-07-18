from ..extensions import db


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    rut_prefix = db.Column(db.Integer)
    rut_suffix = db.Column(db.String(1))
    full_name = db.Column(db.String(200), nullable=False)
    occupation = db.Column(db.String(100), nullable=True)
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
    deceased = db.Column(db.Boolean, default=False)

    sessions = db.relationship('Session', backref='patient', lazy=True)