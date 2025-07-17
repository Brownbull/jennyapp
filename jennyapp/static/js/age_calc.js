// age_calc.js - shared age calculation logic for patient forms

function calculateAge(dateString) {
    const defaultDate = '1900-01-01';
    if (!dateString || dateString === defaultDate) return 0;
    const today = new Date();
    const dob = new Date(dateString);
    if (dob > today) return 0;
    let age = today.getFullYear() - dob.getFullYear();
    const m = today.getMonth() - dob.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
        age--;
    }
    return age;
}

function updateAgeField() {
    const dobInput = document.getElementById('date_of_birth');
    const ageDisplay = document.getElementById('age_display');
    if (!dobInput || !ageDisplay) return;
    let dobValue = dobInput.value;
    let age = calculateAge(dobValue);
    ageDisplay.value = age;
}

function setupAgeField() {
    updateAgeField();
    const dobInput = document.getElementById('date_of_birth');
    if (dobInput) {
        dobInput.addEventListener('change', updateAgeField);
    }
}

document.addEventListener('DOMContentLoaded', setupAgeField);
