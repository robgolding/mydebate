from django import template
from django.conf import settings

register = template.Library()

class MediaURLNode(template.Node):
	def __init__(self, path):
		self.path = path

	def render(self, context):
		import urlparse
		import os.path
		return urlparse.urljoin(settings.MEDIA_URL, self.path);
		return ''

def media(parser, token):
	"""
		Returns an absolute URL pointing to the given media file.

		The first argument is the path to the file starting from MEDIA_ROOT.
		If the file doesn't exist, empty string '' is returned.

		For example if you have the following in your settings:

		MEDIA_URL = 'http://media.example.com'

		then in your template you can get the URL for css/mystyle.css like this:

		{% media 'css/mystyle.css' %}

		This URL will be returned: http://media.example.com/css/style.css.
	"""
	bits = list(token.split_contents())
	if len(bits) != 2:
		raise TemplateSyntaxError("%r tag takes one argument" % bits[0])

	path = bits[1]
	return MediaURLNode(path)
media = register.tag(media)

