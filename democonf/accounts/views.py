from django.http import HttpResponse
from django.contrib import auth

def login(request, *args, **kwargs):
	if request.is_ajax:
		if request.method == 'POST':
			username = request.POST.get('username', '')
			password = request.POST.get('password', '')
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth.login(request, user)
					data = '{"result": true}'
				else:
					data = '{"result": false, "error": "Account disabled."}'
			else:
				data = '{"result": false, "error": "Username/password incorrect."}'
			return HttpResponse(data, mimetype="application/json")
	else:
		return auth.views.login(request, *args, **kwargs)
