from django.db import models

class PollChoiceManager(models.Manager):
	
	def __init__(self, poll):
		self.poll = poll
		self.model = models.get_model("polling", "Choice")
	
	def get_query_set(self):
		Choice = self.model
		return Choice.objects.filter(question=self.poll.question)
