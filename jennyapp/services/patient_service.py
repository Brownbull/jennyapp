from datetime import datetime

from jennyapp.extensions import db
from jennyapp.models.patient import Patient

def get_patient_by_id_or_404(patient_id):
    """Return a Patient object by its id.

    :param patient_id: The id of the Patient to return.
    :return: The Patient with the given id.
    :raises 404: If no Patient with the given id exists.
    """
    return Patient.query.get_or_404(patient_id, description=f'Patient with id {patient_id} not found')

def edit_patient(patient, updated_patient_data):
    """
    Update an existing patient with the provided data.

    :param patient_id: The ID of the patient to update.
    :param updated_patient_data: Dictionary containing updated patient information.
    :return: The updated Patient object.
    """
    for key, value in updated_patient_data.items():
        if key == 'date_of_birth':
            value = datetime.strptime(value, '%Y-%m-%d').date()
        setattr(patient, key, value)
    db.session.commit()
    return patient

def get_patients():
    """Return a list of all patients."""
    return Patient.query.all()

def add_patient(patient_data):
    """
    Create a new patient and add it to the database.

    :param patient_data: Dictionary containing patient information.
    :return: The newly created Patient object.
    """
    new_patient = Patient(**patient_data)
    db.session.add(new_patient)
    db.session.commit()
    return new_patient

def get_patients_full_name_list():
    """Return a list of all patients' full names."""
    return [patient.full_name for patient in get_patients()]

def get_patients_rut_list():
    """Return a list of all patients' RUT prefixes.
        # short version:  
        # return [str(patient.rut_prefix) for patient in Patient.query.filter(Patient.rut_prefix != None).distinct()] """
    rut_list = []
    patients_with_rut = Patient.query.filter(Patient.rut_prefix != None).distinct()

    if patients_with_rut:
        for patient in patients_with_rut:
            rut_list.append(str(patient.rut_prefix))

    return rut_list

def del_patient(patient):
    """
    Deletes a patient from the database.

    :param patient: The patient object to be deleted.
    """
    db.session.delete(patient)
    db.session.commit()

