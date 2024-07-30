from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'sponsor', 'influencer'
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    # Relationships
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)
    
    social_media_links = db.relationship('SocialMediaLink', backref='influencer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), default='public') 
    goals = db.Column(db.Text)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending') 
    messages = db.relationship('Message', backref='ad_request', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    # Define relationships to User model
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])



class SocialMediaLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=False)


