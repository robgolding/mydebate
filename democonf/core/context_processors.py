from django.contrib.sites.models import Site

def site(request):
	site = Site.objects.get_current()
	return {'site': site}
