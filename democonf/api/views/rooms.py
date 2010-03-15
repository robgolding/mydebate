from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room, Message
from democonf.api.views import APIView, APIAuthView

import simplejson

"""Class-based API views for rooms."""

## Some convenience methods for use later on

def get_messages(request, room, unread=False):
	"""Get either all messages, or all *unread* messages for a room. 
	Uses request object to find current user, and marks every message 
	read (a little slow, but hey).
	"""
	if unread:
		messages = room.get_unread_and_mark(request.user)
	else:
		messages = room.get_all_and_mark(request.user)
	return messages


## The actual views

class GetData(APIAuthView):
	def get(self, request, *args, **kwargs):
		"""Get the required data for a room. Returns the following:
			- messages (unread or all)
			- members (username, userid and full name)
			- number of members
			- room mode (conferencing, voting or waiting)
			- time to next vote
		"""
		# API views identify the room via the slug
		slug = request.GET.get('room', None)
		
		if slug is not None:
			# if we've been given a slug, then get the room (or raise a 404 if it doesn't exist)
			room = get_object_or_404(Room, slug=slug)
			
			# add the current user to the list of members in the room
			room.members.add(request.user)
			
			# do we need just the unread messages, or all of them?
			unread = request.GET.get('unread', None)
			unread = unread is not None and unread == "true"
			
			# get the room mode now, as get_mode() does some clever things like posting system messages
			# which we want to happen early
			mode = room.get_mode()
			
			# get the messages for this room, either unread or not
			messages = get_messages(request, room, unread)
			
			# initialise our data lists for use later
			self.data['messages'] = []
			self.data['members'] = []
			
			# stick all messages into the list
			for message in messages:
				self.data['messages'].append({
					'pk': message.pk,
					'author': message.author.username,
					'content': message.content
				})
			
			# do the same with members
			for member in room.members.all():
				self.data['members'].append({
					'pk': member.pk,
					'username': member.username,
					'fullname': member.get_full_name()
				})
			
			# include some extra useful info (number of members, time left, 
			# whether the user created the current room, and what mode we're in at present)
			self.data['num_members'] = len(self.data['members'])
			self.data['time_left'] = room.get_time_to_next_vote()
			self.data['is_creator'] = room.opened_by == request.user
			self.data['is_controller'] = room.controller == request.user
			self.data['current_mode'] = mode
			
			# everything worked, so success is True
			self.data['success'] = True
		
		else:
			# we weren't passed the slug
			self.data['error'] = 'Room ID (slug) required.'
		
		# serialise the data and send it back
		return self.serialise()

get_data = GetData()

class Touch(APIAuthView):
	def get(self, request, *args, **kwargs):
		"""Simple view to 'ping' the room, to signify that the user is still here."""
		slug = request.GET.get('room', None)
		
		# identify the room by slug, and add the user to the current members
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			room.members.add(request.user)
			self.data['success'] = True
		else:
			self.data['error'] = 'Room ID (slug) required.'
	
		return self.serialise()

touch = Touch()

class Reset(APIAuthView):
	def get(self, request, *args, **kwargs):
		"""Reset the room (i.e. make a new poll and start a new period)."""
		slug = request.GET.get('room', None)
		
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			
			# a reset request can only be made by the controller of a room
			if request.user == room.controller:
				room.reset()
				self.data['success'] = True
			else:
				self.data['error'] = 'Only the controller can reset the room.'
		else:
			self.data['error'] = 'Room ID (slug) required.'
	
		return self.serialise()

reset = Reset()

class End(APIAuthView):
	def get(self, request, *args, **kwargs):
		"""End the room (i.e. mark debate as completed, so it no longer shows up on the main list)."""
		slug = request.GET.get('room', None)
		
		if slug is not None:
			room = get_object_or_404(Room, slug=slug)
			
			# debate can only be ended by the controller
			if request.user == room.controller:
				room._set_conferencing_mode(use_this_poll=True)
				room.is_completed = True
				room.save()
				self.data['success'] = True
			else:
				self.data['error'] = 'Only the controller can end the debate.'
		else:
			self.data['error'] = 'Room ID (slug) required.'
	
		return self.serialise()

end = End()

class SendMessage(APIAuthView):
	def post(self, request, *args, **kwargs):
		"""Send a message to a particular room. Returns all unread messages 
		(including the sent message) to save bandwidth and time.
		"""
		slug = request.POST.get('room', None)
		message = request.POST.get('message', '')
		
		if slug is not None:
			if message:
				room = get_object_or_404(Room, slug=slug)
				room.members.add(request.user)
				
				# create and save the new message
				message = Message.objects.create(room=room, author=request.user, content=message)
				message.save()
				
				# get all unread messages for the current user
				messages = get_messages(request, room, True)
				
				self.data['messages'] = []
				
				# put all the messages that were found in a list
				for message in messages:
					self.data['messages'].append({
						'pk': message.pk,
						'author': message.author.username,
						'content': message.content
					})
				
				# everything worked
				self.data['success'] = True
			else:
				# user tried to send an empty message
				self.data['error'] = 'Message content required.'
			
		else:
			self.data['error'] = 'Room ID (slug) required.'
		
		# serialise and send it back!
		return self.serialise()

send_message = SendMessage()
