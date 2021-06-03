celery -A PaperMetrics worker -l info --pool=solo --scheduler django_celery_beat.schedulers:DatabaseScheduler
