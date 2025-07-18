
from jennyapp.models.patient import Patient


def get_patients_full_name_list():
    """Return a list of all patients' full names."""
    return [patient.full_name for patient in Patient.query.all()]

def get_patients_rut_list():
    """Return a list of all patients' RUT prefixes.
        # short version:  
        # return [str(patient.rut_prefix) for patient in Patient.query.filter(Patient.rut_prefix != None).distinct()] """
    patients_with_rut = Patient.query.filter(Patient.rut_prefix != None).distinct()
    rut_list = []
    for patient in patients_with_rut:
        rut_list.append(str(patient.rut_prefix))
    return rut_list