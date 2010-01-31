from django.conf.urls.defaults import *

from models import Room
import views

urlpatterns = patterns('',
	
	url(r'^$', 'django.views.generic.list_detail.object_list', { 'queryset': Room.objects.all(), 'template_name': 'rooms/room_list.html' }, name="rooms_room_list"),
	
	url(r'^(?P<room_id>\d+)/$', views.conference_room, name="rooms_conference_room"),
	
	url(r'^(?P<room_id>\d+)/leave/$', views.leave, name="rooms_leave_room"),
	
	url(r'^create/$', views.create_room, name="rooms_create_room"),
	
)
