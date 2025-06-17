from .extensions import db
from datetime import date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(220), unique=True, nullable=False)
    specialty = db.Column(db.String(120), nullable=True)
    sessions = db.relationship('Session', backref='user', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(220), unique=True, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    rut = db.Column(db.String(30), unique=True, nullable=True)  # National ID
    sessions = db.relationship('Session', backref='patient', lazy=True)

    def age(self):
        if not self.dob:
            return ''
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Float, nullable=True)
