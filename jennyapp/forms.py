from datetime import date, datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, StringField, PasswordField, BooleanField, TextAreaField, DateField, TimeField, EmailField, SelectField, IntegerField, MultipleFileField
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo, Email, Optional

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

chile_regions = ["Región de Arica y Parinacota",
    "Región de Tarapacá",
    "Región de Antofagasta",
    "Región de Atacama",
    "Región de Coquimbo",
    "Región de Valparaíso",
    "Región Metropolitana",
    "Región del Libertador General Bernardo O’Higgins",
    "Región del Maule",
    "Región de Ñuble",
    "Región del Biobío",
    "Región de La Araucanía",
    "Región de Los Ríos",
    "Región de Los Lagos",
    "Región de Aysén del General Carlos Ibáñez del Campo",
    "Región de Magallanes y de la Antártica Chilena",
    "Otra"]

world_countries = ["Afganistán",
    "Albania",
    "Alemania",
    "Andorra",
    "Angola",
    "Antigua y Barbuda",
    "Arabia Saudita",
    "Argelia",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaiyán",
    "Bahamas",
    "Bangladés",
    "Barbados",
    "Baréin",
    "Bélgica",
    "Belice",
    "Benín",
    "Bielorrusia",
    "Birmania",
    "Bolivia",
    "Bosnia y Herzegovina",
    "Botsuana",
    "Brasil",
    "Brunéi",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Bután",
    "Cabo Verde",
    "Camboya",
    "Camerún",
    "Canadá",
    "Catar",
    "Chad",
    "Chile",
    "China",
    "Chipre",
    "Ciudad del Vaticano",
    "Colombia",
    "Comoras",
    "Corea del Norte",
    "Corea del Sur",
    "Costa de Marfil",
    "Costa Rica",
    "Croacia",
    "Cuba",
    "Dinamarca",
    "Dominica",
    "Ecuador",
    "Egipto",
    "El Salvador",
    "Emiratos Árabes Unidos",
    "Eritrea",
    "Eslovaquia",
    "Eslovenia",
    "España",
    "Estados Unidos",
    "Estonia",
    "Etiopía",
    "Filipinas",
    "Finlandia",
    "Fiyi",
    "Francia",
    "Gabón",
    "Gambia",
    "Georgia",
    "Ghana",
    "Granada",
    "Grecia",
    "Guatemala",
    "Guyana",
    "Guinea",
    "Guinea ecuatorial",
    "Guinea-Bisáu",
    "Haití",
    "Honduras",
    "Hungría",
    "India",
    "Indonesia",
    "Irak",
    "Irán",
    "Irlanda",
    "Islandia",
    "Islas Marshall",
    "Islas Salomón",
    "Israel",
    "Italia",
    "Jamaica",
    "Japón",
    "Jordania",
    "Kazajistán",
    "Kenia",
    "Kirguistán",
    "Kiribati",
    "Kuwait",
    "Laos",
    "Lesoto",
    "Letonia",
    "Líbano",
    "Liberia",
    "Libia",
    "Liechtenstein",
    "Lituania",
    "Luxemburgo",
    "Madagascar",
    "Malasia",
    "Malaui",
    "Maldivas",
    "Malí",
    "Malta",
    "Marruecos",
    "Mauricio",
    "Mauritania",
    "México",
    "Micronesia",
    "Moldavia",
    "Mónaco",
    "Mongolia",
    "Montenegro",
    "Mozambique",
    "Namibia",
    "Nauru",
    "Nepal",
    "Nicaragua",
    "Níger",
    "Nigeria",
    "Noruega",
    "Nueva Zelanda",
    "Omán",
    "Países Bajos",
    "Pakistán",
    "Palaos",
    "Panamá",
    "Papúa Nueva Guinea",
    "Paraguay",
    "Perú",
    "Polonia",
    "Portugal",
    "Reino Unido",
    "República Centroafricana",
    "República Checa",
    "República de Macedonia",
    "República del Congo",
    "República Democrática del Congo",
    "República Dominicana",
    "República Sudafricana",
    "Ruanda",
    "Rumanía",
    "Rusia",
    "Samoa",
    "San Cristóbal y Nieves",
    "San Marino",
    "San Vicente y",
    "Granadinas",
    "Santa Lucía",
    "Santo Tomé y Príncipe",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leona",
    "Singapur",
    "Siria",
    "Somalia",
    "Sri Lanka",
    "Suazilandia",
    "Sudán",
    "Sudán del Sur",
    "Suecia",
    "Suiza",
    "Surinam",
    "Tailandia",
    "Tanzania",
    "Tayikistán",
    "Timor Oriental",
    "Togo",
    "Tonga",
    "Trinidad y Tobago",
    "Túnez",
    "Turkmenistán",
    "Turquía",
    "Tuvalu",
    "Ucrania",
    "Uganda",
    "Uruguay",
    "Uzbekistán",
    "Vanuatu",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Yibuti",
    "Zambia",
    "Zimbabue"
]

class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired('Email is required'), Length(max=120), Email(message='Invalid email address.')])
    password = PasswordField('Password', validators=[InputRequired('Password is required'), Length(min=6, max=120, message='Password must be between 6 and 120 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired('Password is required'), EqualTo('password')])

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired('Email is required'), Length(max=120), Email(message='Invalid email address.')])
    password = PasswordField('Password', validators=[InputRequired('Password is required'), Length(min=6, max=120, message='Password must be between 6 and 120 characters')])
    remember_me = BooleanField('Remember Me', default=False)

class PatientForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=200)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', default = date(1900, 1, 1))
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'),  ('other', 'Other'), ], default='other')
    email = EmailField('Email', validators=[Optional(), Length(max=120), Email(message='Invalid email address.')])
    phone_number_1 = StringField('Phone Number', validators=[Length(max=20)])
    phone_number_2 = StringField('Phone Number', validators=[Length(max=20)])
    address_1 = StringField('Address', validators=[Length(max=200)])
    address_2 = StringField('Address 2', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=100)])
    region = SelectField('Region', choices=chile_regions, default=chile_regions[11])
    country = SelectField('Country', choices=world_countries, default=world_countries[37])
    zip_code = StringField('Zip Code', validators=[Length(max=20)])
    notifications = BooleanField('Receive Notifications', default=False)
    # MEDICAL
    medical_history = TextAreaField('Medical History', validators=[Length(max=200)], default='')
    current_medications = TextAreaField('Current Medications', validators=[Length(max=200)], default='')
    allergies = TextAreaField('Allergies', validators=[Length(max=200)], default='')
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Length(max=100)], default='')
    emergency_contact_number = StringField('Emergency Contact Number', validators=[Length(max=20)], default='')
    emergency_contact_relationship = StringField('Emergency Contact Relationship', validators=[Length(max=100)], default='')


class SessionForm(FlaskForm):
    doctor_email = SelectField('Doctor Email', choices=[])
    patient_full_name = SelectField('Patient Full Name', choices=[])
    session_date = DateField('Date', format='%Y-%m-%d', default = date.today())
    session_time = TimeField('Time', format='%H:%M', default = datetime.now().time())
    # MEDICAL
    consent = BooleanField('Consent', default=False)
    reason_for_visit = TextAreaField('Reason for Visit', validators=[DataRequired(), Length(max=200)])
    medications = TextAreaField('Medications', validators=[Length(max=200)], default='')
    diagnostic = TextAreaField('Diagnostic', validators=[Length(max=200)], default='')
    # TRANSACTION
    payment_method = SelectField('Payment Method', choices=[('cash', 'Cash'), ('credit_card', 'Credit Card'), ('debit_card', 'Debit Card')], default='cash')
    total_amount = IntegerField('Total Amount', validators=[Optional()])
    payment_status = SelectField('Payment Status', choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    # FILES
    documents = MultipleFileField('Upload Documents', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf', 'doc', 'docx', 'txt'], 'Images, PDF, Word, TXT only!')])
    
class ProfileForm(FlaskForm):
    about = TextAreaField('About', validators=[Length(max=500)], default='')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Images only!')])
    full_name = StringField('Full Name', validators=[ Length(max=200)])
    email = EmailField('Email', validators=[Optional(), Length(max=120), Email(message='Invalid email address.')])    
    phone_number_1 = StringField('Phone Number', validators=[Length(max=20)])
    phone_number_2 = StringField('Phone Number', validators=[Length(max=20)])
    address_1 = StringField('Address', validators=[Length(max=200)])
    address_2 = StringField('Address 2', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=100)])
    region = SelectField('Region', choices=chile_regions, default=chile_regions[11])
    country = SelectField('Country', choices=world_countries, default=world_countries[37])
    zip_code = StringField('Zip Code', validators=[Length(max=20)])
    notifications = BooleanField('Receive Notifications', default=False)





