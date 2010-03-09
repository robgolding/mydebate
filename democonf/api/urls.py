from django.conf.urls.defaults import *

import views

roomspatterns = patterns('api.views.rooms',
	
	url(r'^get_data/$', 'get_data', name="api_rooms_get_data"),
	
	url(r'^touch/$', 'touch', name="api_rooms_touch"),
	
	url(r'^reset/$', 'reset', name="api_rooms_reset"),
	
	url(r'^end/$', 'end', name="api_rooms_end"),
	
	url(r'^send_message/$', 'send_message', name="api_rooms_send_message"),
	
)

pollingpatterns = patterns('api.views.polling',
	
	url(r'^get_info/$', 'get_info', name="api_polling_get_info"),
	
	url(r'^cast_vote/$', 'cast_vote', name="api_polling_cast_vote"),
	
)

urlpatterns = patterns('',
	
	(r'^rooms/', include(roomspatterns)),
	
	(r'^polling/', include(pollingpatterns)),
	
)
