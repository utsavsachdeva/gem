import os

class Config:
    # Replace 'your-secret-key' with a strong, random key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key' 

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///yourdatabase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_ECHO = True
