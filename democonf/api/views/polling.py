from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room
from democonf.polling.models import Poll, Choice, Vote

from democonf.api.views import APIView, APIAuthView

import simplejson

class GetInfo(APIAuthView):
	def get(request, *args, **kwargs):
		if slug is not None:
			slug = request.GET.get('room', None)
			room = get_object_or_404(Room, slug=slug)
			poll = room.poll
		
			self.data['info'] = {}
			self.data['info']['num_votes'] = poll.get_num_votes()
			self.data['info']['voted'] = poll.has_voted(request.user)
		
			self.data['result'] = True
		else:
			self.data['error'] = "Room ID (slug) required."
	
		return self.serialise()

get_info = GetInfo()

class CastVote(APIAuthView):
	def post(self, request, *args, **kwargs):
		slug = request.POST.get('room', None)
	
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			poll = room.poll
			
			choice_id = request.POST.get('choice', None)
			
			if choice_id is not None:
				choice = get_object_or_404(Choice, pk=choice_id)
				
				vote = Vote(user=request.user, choice=choice)
				vote.save()
				
				self.data = {'result': True}
			else:
				self.data['error'] = "Choice ID required."
		else:
			self.data['error'] = "Room ID (slug) required."
		
		return self.serialise()
		
cast_vote = CastVote()