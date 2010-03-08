from django.db import models
from django.db.models import Sum

from django.contrib.auth.models import User
import managers

class Question(models.Model):
	text = models.CharField(max_length=200)
	
	@property
	def poll(self):
		polls = self.polls.order_by('-created_at')
		if not polls:
			return None
		else:
			return polls[0]
	
	def get_last_poll(self):
		polls = self.polls.order_by('-created_at')
		if len(polls) < 2:
			return None
		else:
			return polls[1]
	
	def reset(self):
		p = Poll(question=self).save()
		return p
	
	def __unicode__(self):
		return self.text

class Poll(models.Model):
	question = models.ForeignKey(Question, related_name="polls")
	created_at = models.DateTimeField(auto_now_add=True)
	
	@property
	def choices(self):
		return self.question.choices
	
	def get_num_votes(self):
		return Vote.objects.filter(poll=self).count()
	
	def get_votes(self):
		return Vote.objects.filter(poll=self)
	
	def get_votes_for(self, choice):
		Vote = models.get_model("polling", "vote")
		return Vote.objects.filter(poll=self, choice=choice)
	
	def get_majority(self):
		max = (None, 0)
		choices = self.choices.all()
		for choice in choices:
			votes = self.get_votes_for(choice).count()
			if votes > max[1]:
				max = (choice, votes)
		
		if max[0] is None:
			return None
		
		for choice in choices:
			if choice != max[0] and self.get_votes_for(choice).count() == max[1]:
				return None
		
		return max
	
	def has_voted(self, user):
		for vote in self.get_votes():
			if vote.user == user:
				return True
		return False
	
	def __unicode__(self):
		return '%s (%s)' % (self.question, self.created_at.strftime("%d/%m/%Y %H:%M"))
	
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices")
    text = models.CharField(max_length=200)
    
    def get_vote_count(self, poll):
    	return self.votes.filter(poll=poll).count()
    
    def __unicode__(self):
    	return self.text

class Vote(models.Model):
	user = models.ForeignKey(User, related_name="votes")
	poll = models.ForeignKey(Poll, related_name="votes")
	choice = models.ForeignKey(Choice, related_name="votes")
	placed_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '%s: %s' % (self.user, self.choice)
