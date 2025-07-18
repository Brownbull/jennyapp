from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user

from ..forms import RegisterForm, LoginForm
from ..services.user_service import add_user, user_email_exists, check_user_credentials

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles the registration of a new user.

    This view function is responsible for rendering the registration form
    and handling the registration of a new user. When the form is submitted,
    the submitted form data is validated. If the form is valid, the data is
    used to create a new user object using the add_user service. The new user
    is then added to the database and the user is logged in.

    :return: Rendered template for the registration form or redirect to the
             dashboard page if the form is valid.
    """
    # Initialize error variable to None
    error = None

    # Create an instance of the RegisterForm
    form = RegisterForm()

    # Check if the form is valid
    if form.validate_on_submit():
        # Check if the email address already exists
        if user_email_exists(form.email.data):
            # If the email address already exists, set the error to be displayed
            error = 'Email address already exists. Please use a different email.'
        else:
            # If the email address doesn't already exist, create a new user using the add_user service
            new_user = add_user(
                email = form.email.data,
                password = form.password.data
            )

            # Log the new user in
            login_user(new_user, remember=False)

            # Redirect the user to the dashboard page
            return redirect(url_for('dashboard.index'))

    # Create a context dictionary to be passed to the template
    context = {
        'form': form,
        'error': error
    }

    # Render the template for the registration form
    return render_template('register.html', **context)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles the login of an existing user.

    This view function is responsible for rendering the login form
    and handling the login of an existing user. When the form is submitted,
    the submitted form data is validated. If the form is valid, the data is
    used to check the user credentials using the check_user_credentials service.
    If the credentials are valid, the user is logged in and redirected to the
    dashboard page.
    """
    # Initialize an error variable to None
    error = None

    # Create an instance of the LoginForm class
    form = LoginForm()

    # Check if the form is being submitted
    if form.validate_on_submit():
        # Use the check_user_credentials service to check the user's credentials
        user = check_user_credentials(form.email.data, form.password.data)

        # If the credentials are invalid, set an error message
        if not user:
            error = 'Invalid username or password'
        else:
            # If the credentials are valid, log the user in
            login_user(user, remember=form.remember_me.data) 

            # Redirect the user to the dashboard page
            return redirect(url_for('dashboard.index'))

    # Create a context dictionary that contains the form and error message
    context = {
        'form': form,
        'error': error,
    }

    # Render the login.html template, passing the context dictionary
    return render_template('login.html', **context)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logs out the current user.

    This view function logs out the currently logged-in user using the
    Flask-Login `logout_user` function and redirects them to the index page.

    :return: Redirect response to the index page.
    """
    logout_user()
    return redirect(url_for('index.index'))