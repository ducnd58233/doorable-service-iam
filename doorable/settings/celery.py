from doorable.env import env

CELERY_BROKER_URL = env.str("BROKER_URL", default="redis://localhost:6379/1")

CELERY_RESULT_BACKEND = "django-cache"

CELERY_TIMEZONE = "UTC"

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_SOFT_TIME_LIMIT = 20  # seconds
CELERY_TASK_TIME_LIMIT = 30  # seconds
CELERY_TASK_MAX_RETRIES = 3
