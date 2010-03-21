from django.conf.urls.defaults import *
from django.conf import settings

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^democonf/', include('democonf.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/(.*)', admin.site.root, name="admin"),
    
    url(r'^$', 'core.views.index', {'template_name': 'index.html'}, name="index"),
    
    (r'^api/', include('democonf.api.urls')),
    
    (r'^rooms/', include('democonf.rooms.urls')),
    
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGOUT_REDIRECT_URL}),
	
	(r'^accounts/', include('registration.urls')),
    
    (r'^users/', include('democonf.users.urls')),
    
    (r'^polling/', include('democonf.polling.urls')),
    
    (r'^search/', include('democonf.search.urls')),
    
    (r'^faq/', include('democonf.faq.urls')),
    
)

if hasattr(settings, 'WORKING_COPY') and settings.WORKING_COPY:
	import os
	try:
		media_path = os.path.join(settings.PATH, 'media')
		urlpatterns += patterns('',
			(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_path}),
		)
	except NameError:
		raise ImproperlyConfigured, "You must define the PATH variable in your local_settings file."
