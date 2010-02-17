from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import simplejson

class APIView(object):
	
	def __init__(self):
		self.data = {'success': False}
	
	def __call__(self, request, *args, **kwargs):
		if request.method == "GET":
			func = self.get
		elif request.method == "POST":
			func = self.post
		
		json = func(request, *args, **kwargs)
		
		return HttpResponse(json, mimetype="application/json")
	
	def get(self, request, *args, **kwargs):
		raise NotImplementedError
	
	def post(self, request, *args, **kwargs):
		raise NotImplementedError
	
	def serialise(self):
		return simplejson.dumps(self.data)

class APIAuthView(APIView):
	
	@login_required
	def __call__(self, request, *args, **kwargs):
		return super(APIAuthView, self).__call__(request, *args, **kwargs)
