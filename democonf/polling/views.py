from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

"""
No views here, the polling system is only accessible via. the API.

API offers the following methods:
	
	- get_info - get information relating to a room's current poll (identified by slug)
	- cast_vote - cast a vote in a room's current poll (again identified by slug)
"""
