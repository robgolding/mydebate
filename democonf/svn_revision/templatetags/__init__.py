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

		try:
			import local_settings
		except:
			if not modified:
				return outS
			else:
				raise Exception, "Modified version of an automatic checkout"
		else:
			if modified:
				return "(Modified working copy)"
			else:
				return "(Unmodified working copy)"
	except:
		return 'Versioning Unavailable'

REVISION = get_revision()
