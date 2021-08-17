import os

class Config:
    """Base configuration variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
