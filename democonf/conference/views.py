from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list

from models import Room, Message

def get_messages(request, room, unread=False):
	if unread:
		messages = room.get_and_mark(request.user)
	else:
		messages = room.messages.all()
	return messages

def get_members(request, room):
	return room.current_members.all()

@login_required
def room(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	room.current_members.add(request.user)
	
	is_ajax = request.is_ajax() or request.GET.get('json', None) == ''
	
	if request.method == "POST":
		m = request.POST.get("message", None)
		if m:
			message = Message.objects.create(room=room, author=request.user, content=m)
			message.save()
		
		if is_ajax:
			object_lists = {}
			message_list = []
			
			for message in get_messages(request, room, True):
				message_list.append({'pk': message.pk, 'author': message.author.username, 'content': message.content})
			object_lists['messages'] = message_list
			
			return render_to_response("conference/serializer.html", {'object_lists': object_lists}, mimetype="application/json")
		else:
			data = {'room': room}
			return render_to_response("conference/room.html", data)
	
	unread = request.GET.get('unread', None) == ''
	
	if is_ajax:
		messages = get_messages(request, room, unread)
		
		object_lists = {}
		objects = {}
		message_list = []
		member_list = []
		
		for message in messages:
			message_list.append({'pk': message.pk, 'author': message.author.username, 'content': message.content})
		object_lists['messages'] = message_list
		
		for member in get_members(request, room):
			member_list.append({'pk': member.pk, 'username': member.username, 'fullname': member.get_full_name()})
		object_lists['members'] = member_list
		
		objects['num_members'] = len(member_list)
		
		return render_to_response("conference/serializer.html", {'object_lists': object_lists, 'objects': objects}, mimetype="application/json")
	
	data = {'room': room}
	return render_to_response("conference/room.html", data)

@login_required
def leave(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	room.current_members.remove(request.user)
	return HttpResponseRedirect(reverse('conference_list'))
