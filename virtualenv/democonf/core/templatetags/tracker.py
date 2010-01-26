import datetime

from django import template
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter
from django.conf import settings
from django.db.models import get_model

star_model = get_model('tracker', 'Star')

register = template.Library()

def starred_for(issue, user):
	return True if star_model.objects.filter(issue=issue, user=user) else False

register.filter(starred_for)

def viewed_by(issue, user):
	return True if user in issue.viewed_by.all() else False

register.filter(viewed_by)

def naturalday(value):
	if not value:
		return u''
	today = datetime.date.today()
	value = datetime.date(value.year, value.month, value.day)
	delta = datetime.timedelta(days=1)
	if value == today:
		return 'today'
	elif value == today + delta:
		return 'tomorrow'
	elif value == today - delta:
		return 'yesterday'
	return None

register.filter(naturalday)

def truncate_chars(s, num):
	"""
	Template filter to truncate a string to at most num characters respecting word
	boundaries.
	"""
	s = force_unicode(s)
	length = int(num)
	if len(s) > length:
		length = length - 3
		if s[length-1] == ' ' or s[length] == ' ':
			s = s[:length].strip()
		else:
			words = s[:length].split()
			if len(words) > 1:
				del words[-1]
			s = u' '.join(words)
		s += ' ...'
	return s
truncate_chars = allow_lazy(truncate_chars, unicode)

def truncatechars(value, arg):
	"""
	Truncates a string after a certain number of characters, but respects word boundaries.

	Argument: Number of characters to truncate after.
	"""
	try:
		length = int(arg)
	except ValueError: # If the argument is not a valid integer.
		return value # Fail silently.
	return truncate_chars(value, length)
truncatechars.is_safe = True
truncatechars = stringfilter(truncatechars)

register.filter(truncatechars)	

def numchars(value):
	return len(str(value))
numchars.is_sage = True

register.filter(numchars)

def paginator(context, adjacent_pages=2):
	"""
	To be used in conjunction with the object_list generic view.

	Adds pagination context variables for use in displaying first, adjacent and
	last page links in addition to those created by the object_list generic
	view.
	"""
	page_numbers = [n for n in \
					range(context["page"] - adjacent_pages, context["page"] + adjacent_pages + 1) \
					if n > 0 and n <= context["pages"]]
	return {
		"hits": context["hits"],
		"results_per_page": context["results_per_page"],
		"page": context["page"],
		"pages": context["pages"],
		"page_numbers": page_numbers,
		"next": context["next"],
		"previous": context["previous"],
		"has_next": context["has_next"],
		"has_previous": context["has_previous"],
		"show_first": 1 not in page_numbers,
		"show_last": context["pages"] not in page_numbers,
	}

register.inclusion_tag("paginator.html", takes_context=True)(paginator)


class IfInNode(template.Node):
	def __init__(self, needle, haystack, nodelist_true, nodelist_false):
		if (needle[0] == needle[-1] and needle[0] in ('"', "'")):
			self.needle = needle[1:-1]
		else:
			self.needle = template.Variable(needle)
			#raise template.TemplateSyntaxError, "%r tag's first argument (needle) should be in quotes" % tag_name
		self.haystack = template.Variable(haystack)
		self.nodelist_true = nodelist_true
		self.nodelist_false = nodelist_false
	
	def render(self, context):
		try:
			if type(self.needle) == template.Variable:
				needle = self.needle.resolve(context)
			else:
				needle = self.needle
		except template.VariableDoesNotExist:
			needle = None
		
		try:
			haystack = self.haystack.resolve(context)
		except template.VariableDoesNotExist:
			haystack = None
		if needle in haystack:
			return self.nodelist_true.render(context)
		else:
			return self.nodelist_false.render(context)

def do_ifin(parser, token):
	try:
		# split_contents() knows not to split quoted strings.
		tag_name, needle, haystack = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires 2 arguments" % token.contents.split()[0]
	
	nodelist_true = parser.parse(('else', 'endifin'))
	token = parser.next_token()
	if token.contents == 'else':
		nodelist_false = parser.parse(('endifin',))
		parser.delete_first_token()
	else:
		nodelist_false = template.NodeList()
	return IfInNode(needle, haystack, nodelist_true, nodelist_false)


register.tag('ifin', do_ifin)
