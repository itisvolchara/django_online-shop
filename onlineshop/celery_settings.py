from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    'send_newsletters': {
        'task': 'main.tasks.send_newsletters',
        'schedule': timedelta(minutes=1),
    },
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_BACKEND = 'redis://localhost:6379/1'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
#add your host of the email here in this case its Gmail so we are going to use Gmail host
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
#add the port number of the email server
EMAIL_PORT = 587
#add your gamil here
EMAIL_HOST_USER = 'volcharaodnonogy@gmail.com'
#add your password here
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL='Celery <naincygupta100@gmail.com>'