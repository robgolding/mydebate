## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room
from democonf.polling.models import Poll, Choice, Vote

from democonf.api.views import APIView, APIAuthView

import simplejson

"""Class-based API views for polling."""

class GetInfo(APIAuthView):
	def get(self, request, *args, **kwargs):
		"""Get the required data for a room's current poll. Returns the following:
			- number of votes
			- whether the current user has voted
			- the poll results (in JSON format, can be rendered into a graph with flot)
			- whether the poll is completed or not (i.e. everyone has voted)
		"""
		# identify the room via the slug
		slug = request.GET.get('room', None)
		if slug is not None:
			# if we have the slug, then get the room and add the user
			# to the current members in that room
			room = get_object_or_404(Room, slug=slug)
			room.members.add(request.user)
			
			# get the current poll object for the given room
			# (i.e. the most recent poll)
			poll = room.question.poll
			
			# initialise our info dictionary
			self.data['info'] = {}
			
			# insert the number of votes
			self.data['info']['num_votes'] = poll.get_num_votes()
			
			# whether the current user has voted or not
			self.data['info']['voted'] = poll.has_voted(request.user)
			
			# initialise our results list
			self.data['results'] = []
			
			# iterate over the choices for the given poll
			for choice in poll.choices.all():
				# for each choice, we put a little dictionary into the results list:
				#	{'label': <choice name>, 'data': <num_votes>}
				# for example:
				#	[{'label': 'Yes', 'data': 2}, {'label': 'No', 'data': 5}]
				self.data['results'].append({'label': choice.text, 'data': poll.get_votes_for(choice).count()})
			
			# has the poll finished or not (>= to account for stray votes that
			# could break the system)
			self.data['completed'] = poll.get_num_votes() >= room.members.count()
			
			# no exceptions so far!
			self.data['success'] = True
		else:
			# we need the slug to identify the room & poll
			self.data['error'] = "Room ID (slug) required."
		
		# serialise the data and send it back
		return self.serialise()

get_info = GetInfo()

class CastVote(APIAuthView):
	def post(self, request, *args, **kwargs):
		"""Cast a vote in the current poll for a given room."""
		# identify the room by it's slug
		slug = request.POST.get('room', None)
	
		if slug is not None:
			# if we have the slug, get the room and it's current poll
			room = get_object_or_404(Room, slug=slug)
			poll = room.question.poll
			
			if room.get_mode() == 'voting':
				# if the room is in voting mode...
				if not poll.has_voted(request.user):
					# AND the current user not not already voted
					
					# get the choice that they wish to vote for
					choice_id = request.POST.get('choice', None)
					
					if choice_id is not None:
						# if we have a choice id then get hold of the Choice object
						choice = get_object_or_404(Choice, pk=choice_id)
						
						# create and save a new vote, cast by the current user,
						# that points to the correct choice and the current poll
						vote = Vote(user=request.user, choice=choice, poll=poll)
						
						# save the vote object
						vote.save()
						
						# all went well, no exceptions
						self.data['result'] = True
					else:
						# the choice ID was not found
						self.data['error'] = "Choice ID required."
				else:
					# user has already voted
					self.data['error'] = "Vote already cast."
			else:
				# room is still in conferencing mode
				self.data['error'] = "Room not in voting mode."
		else:
			# the room's slug wasn't found
			self.data['error'] = "Room ID (slug) required."
		
		# serialise the data and send it back
		return self.serialise()
		
cast_vote = CastVote()
