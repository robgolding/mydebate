from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from democonf.rooms.models import Room, Message

import simplejson

###############################################
## Some convenience methods for use later on ##
###############################################

def get_messages(request, room, unread=False):
	"""Get either all messages, or all *unread* messages for a room. Uses request object to find current user"""
	
	if unread:
		messages = room.get_and_mark(request.user)
	else:
		messages = room.messages.all()
	return messages
	
######################
## The actual views ##
######################

@login_required
def get_data(request):
	"""Get the required data for a room. Returns the following:
		- messages (unread or all)
		- members (username, userid and full name)
		- number of members
		- room mode (conferencing, voting or waiting)
		- time to next vote
	"""
	
	data = {'result': False}
	
	slug = request.GET.get('room', None)
	
	if slug is not None:
		room = get_object_or_404(Room, slug=slug)
		room.current_members.add(request.user)
		
		unread = request.GET.get('unread', None)
		unread = unread is not None and unread == "true"
		
		messages = get_messages(request, room, unread)
		
		data['messages'] = []
		data['members'] = []
		
		for message in messages:
			data['messages'].append({
				'pk': message.pk,
				'author': message.author.username,
				'content': message.content
			})
		
		for member in room.current_members.all():
			data['members'].append({
				'pk': member.pk,
				'username': member.username,
				'fullname': member.get_full_name()
			})
		
		data['num_members'] = len(data['members'])
		data['time_left'] = room.get_time_to_next_vote()
		data['current_mode'] = room.get_mode()
		
		data['result'] = True
		
	else:
		data['error'] = 'Room ID (slug) required.'
	
	json = simplejson.dumps(data)
	
	return HttpResponse(json, mimetype="application/json")

@login_required
def send_message(request):
	"""Send a message to a particular room. Returns all unread messages 
	(including the sent message) to save bandwidth and time.
	"""
	
	data = {'result': False}
	
	if request.method == "POST":
		slug = request.POST.get('room', None)
		message = request.POST.get('message', '')
		
		if slug is not None:
			if message:
				room = get_object_or_404(Room, slug=slug)
				room.current_members.add(request.user)
				
				message = Message.objects.create(room=room, author=request.user, content=message)
				message.save()
				
				messages = get_messages(request, room, True)
				
				data['messages'] = []
				
				for message in messages:
					data['messages'].append({
						'pk': message.pk,
						'author': message.author.username,
						'content': message.content
					})
				
				data['result'] = True
			else:
				data['error'] = 'Message content required.'
			
		else:
			data['error'] = 'Room ID (slug) required.'
		
	else:
		data['error'] = 'Wrong request method.'
	
	json = simplejson.dumps(data)
	
	return HttpResponse(json, mimetype="application/json")
