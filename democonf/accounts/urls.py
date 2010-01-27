from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name="accounts_login"),
	
)
