import os
from celery.schedules import crontab


class config():
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placementportalWT')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///placementportal.db')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'placementportalWT')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_AUTHENTICATION_HEADER = 'Authentication-Token'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes')
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = 'redis://localhost:6379/0'

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 1025))
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')
    ADMIN_REPORT_EMAIL = os.environ.get('ADMIN_REPORT_EMAIL', 'admin@gmail.com')

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_BEAT_SCHEDULE = {
        'daily-reminder': {
            'task': 'Controllers.tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0),
        },
        'monthly-report': {
            'task': 'Controllers.tasks.monthly_report',
            'schedule': crontab(day_of_month=1, hour=10),
        }
    }
