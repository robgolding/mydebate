from django.contrib.sites.models import Site

"""Context processors for the core democonf app."""

def site(request):
	"""Adds the current 'site' to the template context."""
	site = Site.objects.get_current()
	return {'site': site}
