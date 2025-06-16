from flask import Blueprint, render_template, request, redirect, url_for

from jennyapp.models import User
from jennyapp.extensions import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    errors = {}

    if request.method == 'POST':
        email = request.form.get('email')
        
        print(f"Received email: {email}")

        if not email:
            errors['email'] = 'Email is required'
        if not errors:
            print('No errors in input')

    
        user = User(
            email = email
        )

        db.session.add(user)
        db.session.commit()

        print('User added to database:', user)

        return redirect(url_for('main.index'))

    context = {
        'errors': errors
    }
    return render_template('main.html', **context)