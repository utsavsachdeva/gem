from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..forms import AdminUserEditForm, EditCampaignForm, EditAdRequestForm, CategoryForm, SettingsForm
from ..models import db, User, Campaign, AdRequest, Message, Category 
from ..utils import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')




@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """List and manage all users."""
    search_query = request.args.get('search', '')

    # Filter users based on search query
    users = User.query.filter(
        db.or_(
            User.username.ilike(f'%{search_query}%'),  
            User.email.ilike(f'%{search_query}%')      
        )
    ).all()

    return render_template('admin/manage_users.html', users=users)

@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details (admin functionality)."""
    user = User.query.get_or_404(user_id)
    form = AdminUserEditForm(obj=user)

    if form.validate_on_submit():
        # Update user data
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        user.is_flagged = form.is_flagged.data
        user.notes = form.notes.data
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/flag_user/<int:user_id>')
@login_required
@admin_required
def flag_user(user_id):
    """Flag or unflag a user."""
    user = User.query.get_or_404(user_id)
    user.is_flagged = not user.is_flagged  # Toggle flagged status
    db.session.commit()
    flash('User flagged status updated', 'success')
    return redirect(url_for('admin.manage_users'))  # Or redirect to flagged users list

@bp.route('/flagged_users')
@login_required
@admin_required
def flagged_users():
    """List flagged users."""
    users = User.query.filter_by(is_flagged=True).all()
    return render_template('admin/flagged_users.html', users=users)

@bp.route('/campaigns')
@login_required
@admin_required
def manage_campaigns():
    """List all campaigns."""
    search_query = request.args.get('search', '')
    campaigns = Campaign.query.filter(
        db.or_(
            Campaign.name.ilike(f'%{search_query}%'),  
            Campaign.sponsor.has(User.username.ilike(f'%{search_query}%')) 
        )
    ).all()
   
    return render_template('admin/manage_campaigns.html', campaigns=campaigns)


@bp.route('/view_campaign/<int:campaign_id>')
@login_required
@admin_required
def view_campaign(campaign_id):
    """View details of a specific campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)  # Fetch the campaign by ID
    return render_template('admin/view_campaign.html', campaign=campaign)

@bp.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_campaign(campaign_id):
    """Edit campaign details."""
    campaign = Campaign.query.get_or_404(campaign_id)
    form = EditCampaignForm(obj=campaign)

    if form.validate_on_submit():
        # Update the campaign with form data (similar to how you did in edit_user)
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.goals = form.goals.data
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('admin.manage_campaigns'))

    return render_template('admin/edit_campaign.html', campaign=campaign, form=form)

@bp.route('/delete_campaign/<int:campaign_id>')
@login_required
@admin_required
def delete_campaign(campaign_id):
    """Delete a campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('admin.manage_campaigns'))

@bp.route('/ad_requests')
@login_required
@admin_required
def manage_ad_requests():
    """List all ad requests."""
    ad_requests = AdRequest.query.all()
    return render_template('admin/manage_ad_requests.html', ad_requests=ad_requests)

@bp.route('/view_ad_request/<int:ad_request_id>')
@login_required
@admin_required
def view_ad_request(ad_request_id):
    """View details of a specific ad request."""
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('admin/view_ad_request.html', ad_request=ad_request)

@bp.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ad_request(ad_request_id):
    """Edit ad request details (potentially limited for admin)."""
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    influencers = User.query.filter_by(role='influencer').all()  # Get all influencers
    form = EditAdRequestForm(ad_request, influencers)  

    if form.validate_on_submit():
        # Update the ad request with form data
        ad_request.requirements = form.requirements.data
        ad_request.payment_amount = form.payment_amount.data
        # ... (Consider limiting which fields the admin can edit)
        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('admin.manage_ad_requests'))

    return render_template('admin/edit_ad_request.html', ad_request=ad_request, form=form)

@bp.route('/delete_ad_request/<int:ad_request_id>')
@login_required
@admin_required
def delete_ad_request(ad_request_id):
    """Delete an ad request."""
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('admin.manage_ad_requests'))

@bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    """List all categories."""
    categories = Category.query.all()
    return render_template('admin/manage_categories.html', categories=categories)

@bp.route('/add_category', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add a new category."""
    form = CategoryForm() # Assuming you have a CategoryForm

    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))

    return render_template('admin/add_category.html', form=form)

@bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edit category details."""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        # Update the category with form data
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))

    return render_template('admin/edit_category.html', category=category, form=form)

@bp.route('/delete_category/<int:category_id>')
@login_required
@admin_required
def delete_category(category_id):
    """Delete a category."""
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.manage_categories'))

@bp.route('/messages')
@login_required
@admin_required
def manage_messages():
    """View and manage messages between users."""
    messages = Message.query.all() 
    return render_template('admin/manage_messages.html', messages=messages)



@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Display various analytics and statistics."""
    # Example analytics:
    top_categories = db.session.query(Category.name, db.func.count(User.id)).join(User).filter(User.role=='influencer').group_by(Category.name).order_by(db.func.count(User.id).desc()).all()

    top_influencers = db.session.query(User.username, db.func.count(AdRequest.id)).join(AdRequest, User.id==AdRequest.influencer_id).filter(User.role=='influencer').group_by(User.username).order_by(db.func.count(AdRequest.id).desc()).all()
    total_spending = db.session.query(db.func.sum(AdRequest.payment_amount)).filter(AdRequest.status == 'accepted').scalar()
    return render_template('admin/analytics.html', top_categories=top_categories, top_influencers=top_influencers, total_spending=total_spending)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Manage general application settings."""
    # ... Fetch current settings from the database or config file
    form = SettingsForm()  # Create a SettingsForm in your forms.py
    if form.validate_on_submit():
        # ... Update settings in the database or config file based on form data
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', form=form)
