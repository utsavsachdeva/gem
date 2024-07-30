from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from wtforms.validators import DataRequired, ValidationError
from wtforms import FieldList, FormField
from .models import Category, User, AdRequest

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])  # Enforce length restrictions
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')], validators=[DataRequired()])
    submit = SubmitField('Register')


class AdminUserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer'), ('admin', 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active')  
    is_flagged = BooleanField('Flagged') 
    notes = TextAreaField('Notes')
    submit = SubmitField('Update User')

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    budget = IntegerField('Budget', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], default='public') 
    goals = TextAreaField('Goals')
    submit = SubmitField('Create Campaign')

    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('End date must not be before start date.')

class EditCampaignForm(CampaignForm):  # Inherit from CampaignForm
    submit = SubmitField('Update Campaign')

    def __init__(self, campaign, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name.data = campaign.name
        self.description.data = campaign.description
        self.start_date.data = campaign.start_date
        self.end_date.data = campaign.end_date
        self.budget.data = campaign.budget
        self.visibility.data = campaign.visibility
        self.goals.data = campaign.goals

class AdRequestForm(FlaskForm):
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = IntegerField('Payment Amount', validators=[DataRequired()])
    submit = SubmitField('Send Ad Request')

    def __init__(self, campaign_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign_id = campaign_id
        self.influencer_id.choices = [(i.id, i.username) for i in self._get_available_influencers()]

    def _get_available_influencers(self):
        """Helper function to get influencers not already assigned to the campaign."""
        existing_ad_requests = AdRequest.query.filter_by(campaign_id=self.campaign_id).all()
        assigned_influencer_ids = [ar.influencer_id for ar in existing_ad_requests]
        return User.query.filter(User.role == 'influencer', User.id.notin_(assigned_influencer_ids)).all()

    def validate_payment_amount(self, field):
        if field.data <= 0:
            raise ValidationError('Payment amount must be a positive integer.')
        





class EditAdRequestForm(FlaskForm):
  """Form for editing an existing ad request by a sponsor."""
  # The influencer_id field is removed from this form as we do not want sponsors
  # to change the influencer on an existing ad request.

  requirements = TextAreaField('Requirements:', validators=[DataRequired()])
  payment_amount = IntegerField('Payment Amount:', validators=[DataRequired(), NumberRange(min=1, message='Payment must be at least 1')])
  submit = SubmitField('Update Ad Request')

  def __init__(self, ad_request, *args, **kwargs):
      """Initializes the form with the current ad request data."""
      super().__init__(*args, **kwargs)
      self.ad_request = ad_request

      # Pre-populate the form fields with the existing ad request data.
      self.requirements.data = ad_request.requirements
      self.payment_amount.data = ad_request.payment_amount

  def validate_payment_amount(self, field):
      """Custom validation to ensure that the payment amount is a positive integer."""
      if field.data <= 0:
          raise ValidationError('Payment amount must be a positive integer.')






class SocialMediaLinkForm(FlaskForm):
    platform = SelectField('Platform', choices=[('facebook', 'Facebook'), ('instagram', 'Instagram'), ('twitter', 'Twitter'), ('youtube', 'YouTube'), ('linkedin', 'LinkedIn'), ('tiktok', 'TikTok'), ('other', 'Other')])
    url = StringField('URL', validators=[DataRequired()])
class InfluencerProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])

    niche = StringField('Niche', validators=[DataRequired()])
    social_media_links = FieldList(FormField(SocialMediaLinkForm), min_entries=1)  # FieldList for multiple links
    bio = TextAreaField('Bio')
    submit = SubmitField('Update Profile')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]
class CategoryForm(FlaskForm):
    """Form for adding or editing a category."""
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SettingsForm(FlaskForm):
    """Form for managing application settings."""
    site_name = StringField('Site Name', validators=[DataRequired()])
    # Add more fields for other settings as needed (e.g., email, theme, etc.)
    submit = SubmitField('Save Settings')

class AdRequestResponseForm(FlaskForm):
    status = SelectField(
        'Response', 
        choices=[('pending', 'Pending'), ('accepted', 'Accept'), ('rejected', 'Reject'), ('negotiate', 'Negotiate')], 
        validators=[DataRequired()]
    )
    counter_offer = IntegerField('Counter Offer (if negotiating)')
    submit = SubmitField('Submit Response')
