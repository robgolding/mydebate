from django.db import models
from django.db.models import Sum

from django.contrib.auth.models import User
import managers

class Question(models.Model):
	text = models.CharField(max_length=200)
	
	@property
	def poll(self):
		if not self.polls.order_by('-created_at'):
			return None
		else:
			return self.polls.order_by('-created_at')[0]
	
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
    
    def get_vote_count(self):
    	return self.votes.count()
    
    def __unicode__(self):
    	return self.text

class Vote(models.Model):
	user = models.ForeignKey(User, related_name="votes")
	poll = models.ForeignKey(Poll, related_name="votes")
	choice = models.ForeignKey(Choice, related_name="votes")
	placed_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '%s: %s' % (self.user, self.choice)
