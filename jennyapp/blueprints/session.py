from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from ..models import Patient, Session, User, SessionDocument
from ..extensions import db
from ..forms import SessionForm

from jennyapp.services.user_service import get_users_email_list
from jennyapp.services.patient_service import get_patients_full_name_list, get_patient_by_id_or_404
from jennyapp.services.session_service import get_sessions_context, get_session_or_404, get_session_documents, init_session_form_main, update_session, add_session, handle_documents

session_bp = Blueprint('session', __name__, url_prefix='/session')

@session_bp.route('/')
@login_required
def index():
    context = get_sessions_context(request)
    return render_template('dashboard/sessions/ses_index.html', **context)

@session_bp.route('/edit', methods=['GET'])
@session_bp.route('/edit/<int:session_id>', methods=['GET'])
@login_required
def edit_get(session_id = None):
    """
    Handles the GET requests for the session edit form.

    Routes:
        - GET '/edit': Display a form to create a new session.
        - GET '/edit/<int:session_id>': Display a form to edit a specific session.

    Parameters:
        session_id (int, optional): The ID of the session to be edited. Defaults to None.

    Returns:
        Renders the session edit form with the session data if session_id is provided, or a blank form if not.
    """
    rc = None

    form, existing_docs, session_obj, rc = init_session_form_main(session_id)

    context = {
        'error': rc,
        'form': form,
        'session_id': session_id,
        'session_obj': session_obj,
        'existing_docs': existing_docs
    }
    return render_template('dashboard/sessions/ses_edit.html', **context)


@session_bp.route('/edit', methods=['POST'])
@session_bp.route('/edit/<int:session_id>', methods=['POST'])
@login_required
def edit_post(session_id=None):
    error = None
    session_obj = None

    if session_id:
        session_obj = get_session_or_404(session_id)
        form = SessionForm(request.form, obj=session_obj)
    else:
        form = SessionForm(request.form)

    form.doctor_email.choices = get_users_email_list()
    form.patient_full_name.choices = get_patients_full_name_list()

    if form.validate_on_submit():
        if session_obj:
            update_session(session_obj, form)
            delete_ids = request.form.get('delete_documents', '')
            handle_documents(session_obj, form, delete_ids)
        else:
            session_obj = add_session(form)
            handle_documents(session_obj, form, None)
            session_id = session_obj.id
    else:
        error = 'Form validation failed. Please check your input.'

    existing_docs = get_session_documents(session_obj) if session_obj else []

    print("Form errors:", form.errors)

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

