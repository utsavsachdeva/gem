from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

from config import Config   
from .models import db, User # Import the User model here

# Create database instance (but don't initialize it yet)
migrate = Migrate()
login_manager = LoginManager()

# Function to create the Flask app
def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)  # Load configuration from Config class

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Set the login page endpoint
    migrate.init_app(app, db) # Initialize Migrate

    # Register blueprints
    from .blueprints import auth, admin, sponsor, influencer, main
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(sponsor.bp, url_prefix='/sponsor')
    app.register_blueprint(influencer.bp, url_prefix='/influencer')
    app.register_blueprint(main.bp)

    # User loader function should be outside of create_app()
    @login_manager.user_loader
    def load_user(user_id):
        """User loader function for Flask-Login."""
        return User.query.get(int(user_id))  # Fetch the user from the database

    with app.app_context():
        db.create_all() # Create all tables 
        #Print all templates
        print(app.jinja_loader.list_templates())
    return app
