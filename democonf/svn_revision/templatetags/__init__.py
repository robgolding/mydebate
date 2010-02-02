from django.conf import settings

def get_revision():
	import subprocess
	import re, os

	try:
		p = subprocess.Popen('svnversion %s' % os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		outS = p.stdout.read().strip()
		if outS[-1] == 'S':
			switched = True
			outS = outS[:-1]
		modified = True if outS[-1] == 'M' else False

		if getattr(settings, 'WORKING_COPY', False):
			if modified:
				return "(Modified working copy)"
			else:
				return "(Unmodified working copy)"
		else:
			return outS
	except:
		return 'Versioning Unavailable'

REVISION = get_revision()
