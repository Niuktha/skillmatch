import os

class Config:
    SECRET_KEY = os.urandom(24)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'manishd.btech23@rvu.edu.in')  # Set your sender email here
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Dhana@2023')  # Set your sender email password here
