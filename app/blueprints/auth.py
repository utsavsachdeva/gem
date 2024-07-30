from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from ..forms import LoginForm, RegistrationForm
from ..models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Updated Index Route for Auth Blueprint
@bp.route('/')
def index():
    """Index route for the auth blueprint (redirects to login)."""
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Username or email already exists.', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data, role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

 # Import the main blueprint here
# ...

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    form = LoginForm()
    if current_user.is_authenticated:  
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index')) 
    elif form.validate_on_submit(): # validate on submit instead of only if
        user = User.query.filter_by(username=form.username.data).first()  
        if user and user.check_password(form.password.data):
            login_user(user) 
            session['role'] = user.role
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index')) 
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('main.index'))  