from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user
from datetime import datetime

from ..models import User
from ..extensions import db
from ..forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            error = "Email address already exists. Please use a different email."
        else:
            register_user = User(
                email=form.email.data,
                password=form.password.data,
                join_date=datetime.now()
            )
            db.session.add(register_user)
            db.session.commit()
            login_user(register_user, remember=False) 
            return redirect(url_for('dashboard.index'))
        
    context = {
        'form': form,
        'error': error
    }
    return render_template('register.html', **context)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.verify_password(form.password.data):
            error = 'Invalid username or password'
        else:
            login_user(user, remember=form.remember_me.data) 
            return redirect(url_for('dashboard.index'))

    context = {
        'form': form,
        'error': error,
    }
    return render_template('login.html', **context)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))