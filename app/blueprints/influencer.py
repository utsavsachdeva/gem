from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..forms import InfluencerProfileForm, AdRequestResponseForm
from ..models import db, User, AdRequest, Message, Campaign, SocialMediaLink
from ..utils import influencer_required  , flash_errors

bp = Blueprint('influencer', __name__, url_prefix='/influencer')

@bp.route('/')
@login_required
@influencer_required
def index():
    """Redirects to the influencer's ad_requests page."""
    return redirect(url_for('influencer.ad_requests'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
@influencer_required
def profile():
    """View and edit influencer profile."""
    form = InfluencerProfileForm(obj=current_user)
    if form.validate_on_submit():
        try:
            # Update the user's profile data
            current_user.name = form.name.data
            current_user.category_id = form.category.data
            current_user.niche = form.niche.data
            current_user.bio = form.bio.data

            # Update social media links (add, edit, delete)
            # Clear existing links and add new ones
            current_user.social_media_links = []  
            for link_data in form.social_media_links.data:
                link = SocialMediaLink(platform=link_data['platform'], url=link_data['url'])
                current_user.social_media_links.append(link)

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('influencer.profile'))
        except Exception as e:
            db.session.rollback()  # Rollback transaction in case of error
            flash(f'Error updating profile: {str(e)}', 'danger')
    return render_template('influencer/profile.html', form=form)


@bp.route('/ad_requests')
@login_required
@influencer_required
def ad_requests():
    """View all ad requests for the influencer."""
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('influencer/ad_requests.html', ad_requests=ad_requests)

@bp.route('/view_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
@influencer_required
def view_ad_request(ad_request_id):
    """View a specific ad request and allow the influencer to respond."""
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer != current_user:
        abort(403)  

    form = AdRequestResponseForm(obj=ad_request)

    if form.validate_on_submit():
        try:
            # Update the ad request with the response (accept, reject, or negotiate)
            ad_request.status = form.status.data

            if form.status.data == 'negotiate':
                if form.counter_offer.data is not None and form.counter_offer.data > 0: 
                    ad_request.payment_amount = form.counter_offer.data
                else:
                    flash('Invalid counter offer amount.', 'danger')
                    return redirect(url_for('influencer.view_ad_request', ad_request_id=ad_request_id))

                # Create and store message
                message_content = f"Negotiating for ${form.counter_offer.data}"
            else:
                message_content = f"The ad request has been {form.status.data}"

            message = Message(
                ad_request=ad_request,
                sender=current_user, 
                recipient=ad_request.campaign.sponsor,
                content=message_content
            )
            db.session.add(message)
            db.session.commit()

            flash('Response sent successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('influencer.ad_requests')) 


    # Handle invalid form submission (e.g., validation errors)
    else:
        flash_errors(form) 

    return render_template('influencer/view_ad_request.html', ad_request=ad_request, form=form)


@bp.route('/view_campaign/<int:campaign_id>')
@login_required
@influencer_required
def view_campaign(campaign_id):
    """View a public campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.visibility != 'public':
        abort(403)  # Forbidden access if campaign is private
    return render_template('influencer/view_campaign.html', campaign=campaign)

