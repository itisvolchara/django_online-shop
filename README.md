To run celery worker open a separate terminal and run "celery -A onlineshop worker -l info -P gevent"<br>
To run celery beat open a separate terminal and run "celery -A onlineshop beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
