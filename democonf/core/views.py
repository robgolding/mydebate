from django.contrib import messages
from django.template import RequestContext

def index(request, template_name):
	
	if not request.user.is_authenticated():
		messages.add_message(request, messages.INFO, 'First time here? Check out the FAQ.')
	
	data = {}
	return render_to_response(template_name, data, context_instance=RequestContext(context))
