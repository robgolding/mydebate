import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list

from models import Room, Message
from polling.models import Poll, Choice, Question
from forms import PollForm, ChoiceFormSet, RoomForm

@login_required
def conference_room(request, slug):
	"""
	Basic view for a conference room/debate. Adds the current user to the list of user who 
	are 'in' the room at present (which removes them from any other rooms automatically).
	If the room is currently 'inactive' (no users), then it is reset, which sets the countdown
	back to the start of a period, and resets any poll votes that may have been cast previously.
	Login is required, which redirects to login page if user is not authenticated (@login_required).
	"""
	
	room = get_object_or_404(Room, slug=slug)
	
	if not room.is_active():
		room.reset()
		room.controller = request.user
		room.save()
	
	data = {'room': room, 'poll': room.question.poll}
	
	if room.members.add(request.user):
		template = 'rooms/conference_room.html'
	else:
		template = 'rooms/conference_room_error_part.html'
	
	return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def leave(request, slug):
	"""
	Tiny view to allow a user to leave a room - simply removes the user from the current members in 
	that room and redirects to the room list.
	Login is required, which redirects to login page if user is not authenticated (@login_required).
	"""
	room = get_object_or_404(Room.all.all(), slug=slug)
	room.members.remove(request.user)
	if room.is_active():
		m = room.membership_set.order_by('created')[0]
		room.controller = m.user
		room.save()
	return HttpResponseRedirect(reverse('rooms_room_list'))

@login_required
def create_room(request, extra_context={}):
	"""
	View for creating a room. Uses a clever combination of PollForm, RoomForm and ChoiceFormSet to achieve
	3-way model creation:
		- PollForm allows the user to specify the question
		- ChoiceFormSet allows the user to specify an arbitrary number of "choices" to go with the question
			(each one represented by its own DB object)
		- RoomForm gives more advanced "tweaks" for the room, for example:
			- period length (how long each period lasts, default is 30)
			- join threshold (the amount of time that a room is in lock mode before a poll begins)
	"""
	if request.method == "POST":
		# if the user has submitted the form, get the data from all three
		poll_form = PollForm(request.POST, request.FILES)
		choice_formset = ChoiceFormSet(request.POST, request.FILES)
		room_form = RoomForm(request.POST, request.FILES)
		
		if poll_form.is_valid() and choice_formset.is_valid() and room_form.is_valid():
			# if all 3 forms are valid, create a new question object and save it
			q = Question(text=poll_form.cleaned_data['question'])
			q.save()
			
			# create a new poll object that points to the question, and save it
			p = Poll(question=q)
			p.save()
			
			# for every choice the user has inputted
			for form in choice_formset.forms:
				# create a new choice object, and point it at the question created earlier
				c = Choice(question=q, text=form.cleaned_data['choice'])
				c.save()
			
			# finally, create the room itself, pointing to the question object, with the creator of the
			# currently logged in user, and the period length & join threshold as specified in the form
			# data.
			r = Room(question=q, opened_by=request.user, controller=request.user,
				period_length=room_form.cleaned_data['period_length'],
				join_threshold=room_form.cleaned_data['join_threshold'])
			r.save()
			
			# redirect the user to their newly created room
			return HttpResponseRedirect(r.get_absolute_url())
	else:
		# if the user has not submitted the form (i.e. wishes to fill the form in)
		# then initialise the 3 forms with no data
		poll_form = PollForm()
		choice_formset = ChoiceFormSet()
		room_form = RoomForm()
	
	# put the forms into a context dictionary (and update that with any extra context we have been given)
	data = {'poll_form': poll_form, 'choice_formset': choice_formset, 'room_form': room_form}
	data.update(extra_context)
	
	# render the page
	return render_to_response('rooms/room_form.html', data, context_instance=RequestContext(request))
