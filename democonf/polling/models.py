from django.db import models
from django.db.models import Sum

class Poll(models.Model):
	question = models.CharField(max_length=200)
	
	def get_num_votes(self):
		return self.choices.all().aggregate(Sum('votes'))['votes__sum']
	
	def reset(self):
		for choice in self.choices.all():
			choice.votes = 0
			choice.save()
	
	def __unicode__(self):
		return self.question
	
class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __unicode__(self):
    	return self.choice
