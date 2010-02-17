import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list

from models import Room, Message
from polling.models import Poll, Choice
from forms import PollForm, ChoiceFormSet, RoomForm
from decorators import update_status

def get_messages(request, room, unread=False):
	if unread:
		messages = room.get_and_mark(request.user)
	else:
		messages = room.messages.all()
	return messages

def get_members(request, room):
	return room.current_members.all()

@login_required
@update_status
def conference_room(request, slug):
	room = get_object_or_404(Room, slug=slug)
	room.current_members.add(request.user)
	
	if request.method == "POST":
		m = request.POST.get("message", None)
		if m:
			message = Message.objects.create(room=room, author=request.user, content=m)
			message.save()
			
			data = {'room': room}
			return render_to_response("rooms/conference_room.html", data, context_instance=RequestContext(request))
	
	data = {'room': room, 'poll': room.poll}
	return render_to_response("rooms/conference_room.html", data, context_instance=RequestContext(request))

@login_required
@update_status
def leave(request, slug):
	room = get_object_or_404(Room, slug=slug)
	room.current_members.remove(request.user)
	return HttpResponseRedirect(reverse('rooms_room_list'))

@login_required
def create_room(request, extra_context={}):
	if request.method == "POST":
		poll_form = PollForm(request.POST, request.FILES)
		choice_formset = ChoiceFormSet(request.POST, request.FILES)
		room_form = RoomForm(request.POST, request.FILES)
		if poll_form.is_valid() and choice_formset.is_valid() and room_form.is_valid():
			p = Poll(question=poll_form.cleaned_data['question'])
			p.save()
			for form in choice_formset.forms:
				print form.cleaned_data
				c = Choice(poll=p, choice=form.cleaned_data['choice'])
				c.save()
			r = Room(poll=p, opened_by=request.user, period_length=room_form.cleaned_data['period_length'],
				join_threshold=room_form.cleaned_data['join_threshold'])
			r.save()
			return HttpResponseRedirect(r.get_absolute_url())
	else:
		poll_form = PollForm()
		choice_formset = ChoiceFormSet()
		room_form = RoomForm()
	data = {'poll_form': poll_form, 'choice_formset': choice_formset, 'room_form': room_form}
	data.update(extra_context)
	return render_to_response('rooms/room_form.html', data, context_instance=RequestContext(request))
