from functools import wraps
from flask import abort, flash, redirect, url_for, session  # Import session
from flask_login import current_user
from .models import AdRequest
def admin_required(func):
    """Decorator to restrict access to admin-only views."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or session.get('role') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login page
        return func(*args, **kwargs)
    return decorated_view


def sponsor_required(func):
    """Decorator to restrict access to sponsor-only views."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or session.get('role') != 'sponsor':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))

        # Additional check for ad request editing
        if 'ad_request_id' in kwargs:
            ad_request_id = kwargs['ad_request_id']
            ad_request = AdRequest.query.get(ad_request_id)
            if ad_request is None or ad_request.campaign.sponsor != current_user:
                abort(403)  # Forbidden access if not owner or ad request doesn't exist
        
        return func(*args, **kwargs)
    return decorated_view

def influencer_required(func):
    """Decorator to restrict access to influencer-only views."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or session.get('role') != 'influencer':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login page
        return func(*args, **kwargs)
    return decorated_view


# Other utility functions (optional)
def flash_errors(form):
    """Flashes form errors to the user."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
