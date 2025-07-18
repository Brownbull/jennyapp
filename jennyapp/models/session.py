from ..extensions import db

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
    symptoms = db.Column(db.String(200), nullable=True)
    medications = db.Column(db.String(200), nullable=True)
    treatment = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
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