from django.conf.urls.defaults import *

from models import Room
import views

urlpatterns = patterns('',
	
	url(r'^$', 'django.views.generic.list_detail.object_list', { 'queryset': Room.objects.all(), 'template_name': 'conference/room_list.html' }, name="conference_room_list"),
	
	url(r'^(?P<room_id>\d+)/$', views.room, name="conference_room"),
	
	url(r'^(?P<room_id>\d+)/leave/$', views.leave, name="conference_room_leave"),
	
)
