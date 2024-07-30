from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..forms import CampaignForm, EditCampaignForm, AdRequestForm, EditAdRequestForm
from ..models import db, Campaign, AdRequest, User, Message
from ..utils import sponsor_required  # Assuming you have a sponsor_required decorator for authorization

# sponsor.py
bp = Blueprint('sponsor', __name__, url_prefix='/sponsor')  # Remove template_folder

@bp.route('/campaigns')
@login_required
@sponsor_required
def campaigns():
    """Displays a list of the sponsor's campaigns."""
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    return render_template('sponsor/campaigns.html', campaigns=campaigns)

@bp.route('/create_campaign', methods=['GET', 'POST'])
@login_required
@sponsor_required
def create_campaign():
    """Creates a new campaign."""
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            campaign = Campaign(
                name=form.name.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                budget=form.budget.data,
                visibility=form.visibility.data,
                goals=form.goals.data,
                sponsor_id=current_user.id
            )
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully!', 'success')
            return redirect(url_for('sponsor.campaigns'))
        except Exception as e:  # Catch any unexpected errors
            db.session.rollback()
            flash('An error occurred while creating the campaign.', 'danger')
    return render_template('sponsor/create_campaign.html', form=form)

@bp.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
@sponsor_required
def edit_campaign(campaign_id):
    """Edits an existing campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor != current_user:
        abort(403)  # Forbidden access if not the campaign owner

    form = EditCampaignForm(obj=campaign)
    if form.validate_on_submit():
        try:
            # Update campaign fields
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.start_date = form.start_date.data
            campaign.end_date = form.end_date.data
            campaign.budget = form.budget.data
            campaign.visibility = form.visibility.data
            campaign.goals = form.goals.data
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('sponsor.campaigns'))
        except Exception as e:  # Catch any unexpected errors
            db.session.rollback()
            flash('An error occurred while updating the campaign.', 'danger')
    return render_template('sponsor/edit_campaign.html', campaign=campaign, form=form)


@bp.route('/delete_campaign/<int:campaign_id>')
@login_required
@sponsor_required
def delete_campaign(campaign_id):
    """Deletes a campaign and its associated ad requests."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor != current_user:
        abort(403)  # Forbidden access if not the campaign owner

    try:
        # Manually delete associated ad requests
        AdRequest.query.filter_by(campaign_id=campaign_id).delete()

        # Delete the campaign itself
        db.session.delete(campaign)
        db.session.commit()

        flash('Campaign and associated ad requests deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the campaign: {str(e)}', 'danger')

    return redirect(url_for('sponsor.campaigns'))


@bp.route('/ad_requests/<int:campaign_id>')
@login_required
@sponsor_required
def ad_requests(campaign_id):
    """Displays ad requests for a specific campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor != current_user:
        abort(403)  # Forbidden access if not the campaign owner

    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    return render_template('sponsor/ad_requests.html', ad_requests=ad_requests, campaign=campaign)

@bp.route('/create_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
@sponsor_required
def create_ad_request(campaign_id):
    """Creates a new ad request for a specific campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor != current_user:
        abort(403) 

    form = AdRequestForm(campaign_id=campaign_id)

    # Populate influencer choices dynamically from the database
    influencers = User.query.filter_by(role='influencer').all()
    form.influencer_id.choices = [(i.id, i.username) for i in influencers]

    if form.validate_on_submit():
        try:
            ad_request = AdRequest(
                campaign_id=campaign_id,
                influencer_id=form.influencer_id.data,
                requirements=form.requirements.data,
                payment_amount=form.payment_amount.data,
            )
            db.session.add(ad_request)
            db.session.commit()
            flash('Ad request created successfully!', 'success')
            return redirect(url_for('sponsor.ad_requests', campaign_id=campaign_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the ad request.', 'danger')
    return render_template('sponsor/create_ad_request.html', form=form, campaign=campaign)


@bp.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
@sponsor_required
def edit_ad_request(ad_request_id):
    """Edits an existing ad request."""

    print("current user role in edit_ad_request", current_user.role)
    print("ad request id", ad_request_id)
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    # Check if sponsor owns the campaign
    if ad_request.campaign.sponsor != current_user:
        abort(403)  

    form = EditAdRequestForm(obj=ad_request) 

    if form.validate_on_submit():
        try:
            # Update the ad request with form data
            ad_request.requirements = form.requirements.data
            ad_request.payment_amount = form.payment_amount.data
            # removed ad_request.influencer_id = form.influencer_id.data  

            # Add a message to notify the influencer
            message = Message(
                ad_request=ad_request,
                sender=current_user,
                recipient=ad_request.influencer,
                content="The ad request has been updated. Please review."
            )
            db.session.add(message)
            
            db.session.commit()
            flash('Ad request updated successfully!', 'success')
            return redirect(url_for('sponsor.ad_requests', campaign_id=ad_request.campaign_id))
        except Exception as e:  # Add error handling
            db.session.rollback()
            flash(f'An error occurred while updating the ad request: {str(e)}', 'danger')

    return render_template('sponsor/edit_ad_request.html', ad_request=ad_request, form=form)



@bp.route('/delete_ad_request/<int:ad_request_id>')
@login_required
@sponsor_required
def delete_ad_request(ad_request_id):
    """Deletes an ad request."""
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor != current_user:
        abort(403)
    try:
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the ad request.', 'danger')
    return redirect(url_for('sponsor.ad_requests', campaign_id=ad_request.campaign_id))
