from flask import Blueprint, render_template, url_for, redirect, request, current_app, abort
from flask_login import login_user, logout_user, current_user, login_required, logout_user

from .extensions import db
from .forms import RegisterForm, LoginForm
from .models import User

main = Blueprint('main', __name__)
@main.route('/')
def index():
    errors = {}
    form = LoginForm()

    context = {
        'errors': errors,
        'form': form
    }
    return render_template('index.html', **context)

@main.route('/register', methods=['GET', 'POST'])
def register():
    errors = {}
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        specialty = form.specialty.data

        login_user(new_user, remember=False)
        new_user = User(email=email, password=password, specialty=specialty)
        db.session.add(new_user)
        db.session.commit()

        return "<h1>Registered user: {{ new_user.email }}</h1>"
        # return redirect(url_for('main.profile'), **context)

    context = {
        'errors': errors,
        'form': form
    }
    return render_template('register.html', **context)

@main.route('/login', methods=['GET', 'POST'])
def login():
    
    error = None
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user or not user.verify_password(password):
            error = "Invalid email address or password. Please try again."

        if error:
            return render_template('login.html', error=error)
        else:
            login_user(user, remember = form.remember.data)
            return redirect(url_for('main.profile'))
  
    return render_template('login.html', form=form)

@main.route('/profile')
def profile():
    return render_template('profile.html')




@main.route('/timeline')
def timeline():
    return "<h1>timeline</h1>"

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
