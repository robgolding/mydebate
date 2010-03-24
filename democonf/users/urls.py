from django.conf.urls.defaults import *

from django.contrib.auth.models import User

import profiles.views

import views

# Generic list_detail views
urlpatterns = patterns('django.views.generic',
	
	url(r'^$', 'list_detail.object_list', {'queryset': User.objects.exclude(username='system').order_by('username'), 'template_name': 'users/user_list.html', 'extra_context': {'tab': 'users'}}, name='users_user_list'),
	
)


urlpatterns += patterns('',
	
	url(r'^edit/(?P<username>.+)/$', views.edit_user, {'template_name': 'users/edit_user.html', 'extra_context': {'tab': 'users'}}, name='users_edit_user'),
	
	url(r'^(?P<username>.+)/$', views.user_detail, {'template_name': 'users/user_detail.html', 'extra_context': {'tab': 'users'}}, name='users_user_detail'),
	
	url(r'^(?P<username>.+)/$', views.user_detail, {'template_name': 'users/user_detail.html', 'extra_context': {'tab': 'users'}}, name='profiles_profile_detail'),	
)
