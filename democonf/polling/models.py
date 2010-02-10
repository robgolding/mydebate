from django.db import models
from django.db.models import Sum

from django.contrib.auth.models import User

class Poll(models.Model):
	question = models.CharField(max_length=200)
	
	def get_num_votes(self):
		return self.choices.all().aggregate(Sum('votes'))['votes__sum']
	
	def reset(self):
		for choice in self.choices.all():
			for vote in choice.votes.all():
				vote.delete()
	
	def __unicode__(self):
		return self.question
	
class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=200)
    
    def get_vote_count(self):
    	return self.votes.count()
    
    def __unicode__(self):
    	return self.choice

class Vote(models.Model):
	user = models.ForeignKey(User, related_name="votes")
	choice = models.ForeignKey(Choice, related_name="votes")
	placed_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '[Vote] %s' % self.choice
