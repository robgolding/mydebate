from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
	
	url(r'^vote/(?P<poll_id>\d+)/$', views.vote, name="polling_vote"),
	
)
