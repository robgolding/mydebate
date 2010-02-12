from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room
from democonf.polling.models import Poll, Choice, Vote

import simplejson

@login_required
def get_info(request):
	"""
	Get information about a poll. Returns the following:
		- number of votes
		- whether the current user has voted or not
	"""
	
	data = {'result': False}
	
	slug = request.GET.get('room', None)

	if slug is not None:
		room = get_object_or_404(Room, slug=slug)
		poll = room.poll
		
		data['info'] = {}
		data['info']['num_votes'] = poll.get_num_votes()
		data['info']['voted'] = poll.has_voted(request.user)
		
		data['result'] = True
	else:
		data['error'] = "Room ID (slug) required."
	
	json = simplejson.dumps(data)
	
	return HttpResponse(json, mimetype="application/json")

@login_required
def cast_vote(request):
	"""
	Vote on a poll identified by a slug (which points to a Room object).
	Returns the standard 'result' variable in JSON format as standard, with an error if the 
	method failed.
	"""
	
	data = {'result': False}
	
	if request.method == 'POST':
		slug = request.POST.get('room', None)
	
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			poll = room.poll
			
			choice_id = request.POST.get('choice', None)
			
			if choice_id is not None:
				choice = get_object_or_404(Choice, pk=choice_id)
				
				vote = Vote(user=request.user, choice=choice)
				vote.save()
				
				data = {'result': True}
			else:
				data['error'] = "Choice ID required."
		else:
			data['error'] = "Room ID (slug) required."
	else:
		data['error'] = "Wrong request method."
	
	json = simplejson.dumps(data)
	
	return HttpResponse(json, mimetype="application/json")
