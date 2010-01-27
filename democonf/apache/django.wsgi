import os
import sys
import site

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

site.addsitedir(os.path.join(root_dir, 'lib/python2.6/site-packages'))

sys.path.append(root_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'democonf.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
