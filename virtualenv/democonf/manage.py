#!/usr/bin/env python
import sys

from os.path import abspath, dirname, join
from site import addsitedir

from django.conf import settings
from django.core.management import setup_environ, execute_from_command_line, get_commands, execute_manager
from django.core.management.commands.startapp import ProjectCommand

try:
    import settings as settings_mod # Assumed to be in the same directory
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" %__file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings
setup_environ(settings_mod)

prev_sys_path = list(sys.path)

# define paths to work on
BASE_PATH = abspath(join(abspath(dirname(__file__)), '..'))
LIB_PATH = join(BASE_PATH, 'env', 'lib', 'python2.6')
SITE_PACKAGES_PATH = join(LIB_PATH, 'site-packages')

# add libs and pluggables to our python path
for d in (LIB_PATH, SITE_PACKAGES_PATH):
    path = addsitedir(d, set())
    if path:
    	    sys.path = list(path) + sys.path

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
	if item not in prev_sys_path:
		new_sys_path.append(item)
		sys.path.remove(item)
sys.path[:0] = new_sys_path

# make sure that project's manage.py command creates new apps inside the right directory
cmds = get_commands()
cmds['startapp'] = ProjectCommand(settings.PATH)

if __name__ == '__main__':
    #execute_from_command_line()
    execute_manager(settings_mod)
