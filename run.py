from app import create_app
from app.models import db
from flask.cli import FlaskGroup

# Create the app
app = create_app()

# Create a FlaskGroup for CLI commands
cli = FlaskGroup(app=app)

# Database creation is already handled in __init__.py, so no need to repeat here

# Run the application
if __name__ == '__main__':
    cli() 
