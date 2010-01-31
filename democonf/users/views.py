from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from profiles.views import profile_detail, edit_profile

from models import *

def user_detail(request, *args, **kwargs):
	user = get_object_or_404(User, username=kwargs['username'])
	try:
		user.get_profile()
	except:
		Profile(user=user).save()
	return profile_detail(request, *args, **kwargs)

def edit_user(request, *args, **kwargs):
	user = get_object_or_404(User, username=kwargs['username'])
	if request.user != user:
		return HttpResponseRedirect(reverse('users_user_detail', kwargs={'username': kwargs['username']}))
	else:
		del kwargs['username']
		return edit_profile(request, *args, **kwargs)
