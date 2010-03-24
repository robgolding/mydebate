## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.conf import settings

def get_revision():
	import subprocess
	import re, os

	try:
		p = subprocess.Popen('svnversion %s' % os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		outS = p.stdout.read().strip()
		parts = outS.split(":")
		if len(parts) > 1:
			rev = parts[1]
		else:
			rev = outS
		modified = True if outS[-1] == 'M' else False
		return rev
	except:
		return 'Versioning Unavailable'

REVISION = get_revision()
