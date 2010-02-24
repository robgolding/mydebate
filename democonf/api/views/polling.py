from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room
from democonf.polling.models import Poll, Choice, Vote

from democonf.api.views import APIView, APIAuthView

import simplejson

class GetInfo(APIAuthView):
	def get(self, request, *args, **kwargs):
		slug = request.GET.get('room', None)
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			poll = room.question.poll
		
			self.data['info'] = {}
			self.data['info']['num_votes'] = poll.get_num_votes()
			self.data['info']['voted'] = poll.has_voted(request.user)
			
			self.data['results'] = []
			for choice in poll.choices.all():
				self.data['results'].append({'label': choice.text, 'data': choice.votes.count()})
			
			self.data['results']
			
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
			poll = room.question.poll
			
			if not poll.has_voted(request.user):
			
				choice_id = request.POST.get('choice', None)
			
				if choice_id is not None:
					choice = get_object_or_404(Choice, pk=choice_id)
				
					vote = Vote(user=request.user, choice=choice, poll=poll)
					vote.save()
				
					self.data = {'result': True}
				else:
					self.data['error'] = "Choice ID required."
			else:
				self.data['error'] = "Vote already cast."
		else:
			self.data['error'] = "Room ID (slug) required."
		
		return self.serialise()
		
cast_vote = CastVote()
