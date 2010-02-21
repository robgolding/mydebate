from django.conf import settings

STALE_USER_TIMEOUT = getattr(settings, 'STALE_USER_TIMEOUT', 20)
