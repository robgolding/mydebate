## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.conf.urls.defaults import *
from django.conf import settings

import views

urlpatterns = patterns('',
    
    url(r'^login/$', 'django.contrib.views.login', {'template_name': 'accounts/login.html'}, name="accounts_login"),
	
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGOUT_REDIRECT_URL}, name="accounts_logout"),
	
)
