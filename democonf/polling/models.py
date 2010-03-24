## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.db import models
from django.db.models import Sum

from django.contrib.auth.models import User

"""Models for the 'polling' app:
	
	- Question
	- Poll
	- Choice
	- Vote

"""

class Question(models.Model):
	"""Simple model to represent a question. Simply extracts the common data from
	all polls (the text of the question), to save copying it each time.
	"""
	text = models.CharField(max_length=200)
	
	@property
	def poll(self):
		"""Get the latest poll that relates to this question.
		Makes using the API simple:
			
			room.question.poll
			
		"""
		polls = self.polls.order_by('-created_at')
		if not polls:
			# there aren't any polls!
			return None
		else:
			# return the first poll when they are sorted in time order, decending
			# (i.e. the most recent one)
			return polls[0]
	
	def get_last_poll(self):
		"""Get the last poll that completed"""
		polls = self.polls.order_by('-created_at')
		
		if len(polls) < 2:
			# there aren't any polls that have finished yet
			return None
		else:
			# return the previous one
			return polls[1]
	
	def reset(self):
		"""Reset the question. Creates a new poll object, which then automatically becomes the
		latest and therefore current poll.
		"""
		# create the new poll
		p = Poll(question=self)
		
		# save and return it
		p.save()
		return p
	
	def __unicode__(self):
		"""Unicode representation:
			
			Does God Exist?
			
		"""
		return self.text

class Poll(models.Model):
	"""Simple model for a Poll. Points to the question, and stores when it was created."""
	question = models.ForeignKey(Question, related_name="polls")
	created_at = models.DateTimeField(auto_now_add=True)
	
	@property
	def choices(self):
		"""Get all the choices for this poll. Traverses *up* the chain
		to the question first, then back down to all the questions for that choice.
		Makes the API *much* easier to use!
		"""
		return self.question.choices
	
	def get_num_votes(self):
		"""Count the number of votes that have been cast for this poll so far."""
		return Vote.objects.filter(poll=self).count()
	
	def get_votes(self):
		"""Get all the vote objects for this poll so far."""
		return Vote.objects.filter(poll=self)
	
	def get_votes_for(self, choice):
		"""Get all the vote objects for a particular choice on this poll."""
		Vote = models.get_model("polling", "vote")
		return Vote.objects.filter(poll=self, choice=choice)
	
	def get_majority(self):
		"""Get the majority vote for this poll. Returns a tuple containing the choice
		that received the majority vote, and the number of votes that choice received.
		E.g.:
			
			(<Choice: Yes>, 5)
		
		"""
		
		# initially, there is no maximum
		max = (None, 0)
		
		# all choices that are available in this poll
		choices = self.choices.all()
		
		for choice in choices:
			# number of votes for this choice, compared to the previous maximum
			votes = self.get_votes_for(choice).count()
			if votes > max[1]:
				max = (choice, votes)
		
		# if we didn't find a maximum (none were above 0 votes)
		# then we return None (no majority)
		if max[0] is None:
			return None
		
		# second pass over the choices
		for choice in choices:
			# if there are 2 maximums that are equal, then there is no majority
			# so return None
			if choice != max[0] and self.get_votes_for(choice).count() == max[1]:
				return None
		
		# return the majority we found in the first pass
		return max
	
	def has_voted(self, user):
		"""Find out if the given user has voted on this poll yet."""
		for vote in self.get_votes():
			if vote.user == user:
				return True
		return False
	
	def __unicode__(self):
		"""Unicode representation:
			
			Does God Exist (02/02/2010 16:39)
		
		"""
		return '%s (%s)' % (self.question, self.created_at.strftime("%d/%m/%Y %H:%M"))
	
class Choice(models.Model):
	"""Model to represent a choice for a given question (and therefore Poll)."""
	question = models.ForeignKey(Question, related_name="choices")
	text = models.CharField(max_length=200)
	
	def get_vote_count(self, poll):
		"""Count the number of votes for this choice, on a given poll."""
		return self.votes.filter(poll=poll).count()
	
	def __unicode__(self):
		"""Unicode representation is simply the text:

		Yes

		"""
		return self.text

class Vote(models.Model):
	"""Model to represent a vote that has been cast.
	Stores the user that cast the vote, the poll + choice that was voted upon, and the time at which
	the vote was cast.
	"""
	user = models.ForeignKey(User, related_name="votes")
	poll = models.ForeignKey(Poll, related_name="votes")
	choice = models.ForeignKey(Choice, related_name="votes")
	placed_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		"""Unicode representation, e.g.:
			
			rob: Yes
		
		"""
		return '%s: %s' % (self.user, self.choice)
