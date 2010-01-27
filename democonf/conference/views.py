from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list

from models import Room, Message

@login_required
def room(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	room.current_members.add(request.user)
	
	if request.GET.get('json', None) == '':
		if request.GET.get('unread', None) == '':
			messages = room.get_and_mark(request.user)
		else:
			messages = room.messages.all()
		
		object_lists = {}
		message_list = []
		member_list = []
		
		for message in messages:
			message_list.append({'pk': message.pk, 'author': message.author.username, 'content': message.content})
		object_lists['messages'] = message_list
		
		for member in room.current_members.all():
			member_list.append({'pk': member.pk, 'username': member.username, 'fullname': member.get_full_name()})
		object_lists['members'] = member_list
		
		return render_to_response("conference/serializer.html", {'object_lists': object_lists}, mimetype="application/json")
	
	if request.method == "POST":
		m = request.POST.get("message")
		if m:
			message = Message.objects.create(room=room, author=request.user, content=m)
			message.save()
	
	data = {'room': room}
	return render_to_response("conference/room.html", data)

@login_required
def leave(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	room.current_members.remove(request.user)
	return HttpResponseRedirect(reverse('conference_list'))

@login_required
def messages(request, room_id):
	room = get_object_or_404(Room, pk=room_id)	
	
	if request.GET.get('unread', None) == '':
		messages = room.get_and_mark(request.user)
	else:
		messages = room.messages.all()
	
	if request.is_ajax() or request.GET.get('json', None) == '':
		mlist = []
		for message in messages:
			mlist.append({'pk': message.pk, 'author': message.author.username, 'content': message.content})
		return render_to_response("conference/serializer.html", {'object_list': mlist}, mimetype="application/json")

	data = {'room': room, 'messages': messages}
	return render_to_response("conference/messages.html", data)

@login_required
def members(request, room_id):
	room = get_object_or_404(Room, pk=room_id)
	members = room.current_members.all()
	
	if request.is_ajax() or request.GET.get('json', None) == '':
		mlist = []
		for member in members:
			mlist.append({'pk': member.pk, 'username': member.username, 'fullname': member.get_full_name()})
		return render_to_response("conference/serializer.html", {'object_list': mlist}, mimetype="application/json")
	
	data = {'room': room, 'members': members}
	return render_to_response("conference/members.html", data)
