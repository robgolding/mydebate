from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    
    url(r'^login/$', views.login, {'template_name': 'accounts/login.html'}, name="accounts_login"),
	
	url(r'^logout/$', 'django.contrib.auth.views.logout', {}, name="accounts_logout"),
	
)
