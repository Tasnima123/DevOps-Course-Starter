import os

class Config:
    """Base configuration variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LOG_LEVEL = os.environ.get('LOG_LEVEL')
    LOGGLY_TOKEN = os.environ.get('LOGGLY_TOKEN')
    
