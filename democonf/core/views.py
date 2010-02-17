from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request, template_name):
	data = {}
	return render_to_response(template_name, data, context_instance=RequestContext(request))
