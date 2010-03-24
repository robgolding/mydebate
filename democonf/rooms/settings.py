## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.conf import settings

STALE_USER_TIMEOUT = getattr(settings, 'STALE_USER_TIMEOUT', 10)
