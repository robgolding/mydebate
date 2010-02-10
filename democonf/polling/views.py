from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from models import Poll, Choice, Vote

@login_required
def vote(request, poll_id):
	poll = get_object_or_404(Poll, pk=poll_id)
	
	if request.method == 'POST':
		choice_id = request.POST.get('choice', None)
		
		if choice_id is not None:
			choice = get_object_or_404(Choice, pk=choice_id)
			
			vote = Vote(user=request.user, choice=choice)
			vote.save()
			
			return HttpResponse("Vote cast successfully.")
		else:
			return HttpResponse("Choice required.")
	else:
		return HttpResponse("Wrong request method.")
