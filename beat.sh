celery -A PaperMetrics beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
