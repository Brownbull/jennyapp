from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict

from ..models import Patient, Session, User, SessionDocument
from ..extensions import db
from ..forms import SessionForm

from jennyapp.services.user_service import get_users_email_list
from jennyapp.services.patient_service import get_patients_full_name_list, get_patient_by_id_or_404
from jennyapp.services.session_service import apply_form_obj, del_session, get_form_obj_from_request, get_sessions_context, get_session_or_404, get_session_documents, get_form_by_id, get_form, update_session, add_session, handle_documents

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
    if session_id:
        form, existing_docs, session_obj = get_form_by_id(session_id)
    else:
        form, existing_docs, session_obj = get_form()

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

    form, session_obj, error = get_form_obj_from_request(session_id)

    if form.validate_on_submit():
        apply_form_obj(form, session_obj)
        return redirect(url_for('session.index', doctor=current_user.email))
    else:
        error = form.errors

    existing_docs = get_session_documents(session_obj)

    context = {
        'error': error,
        'form': form,
        'session_id': session_obj.id,
        'session_obj': session_obj,
        'existing_docs': existing_docs,
    }
    return render_template('dashboard/sessions/ses_edit.html', **context)

@session_bp.route('/delete/<int:session_id>', methods=['GET', 'POST'])
@login_required
def delete(session_id):
    del_session(session_id)
    return redirect(url_for('session.index', doctor=current_user.email))

