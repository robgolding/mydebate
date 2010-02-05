import datetime

from django.db import models
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

Poll = models.get_model("polling", "poll")

from polling.models import Poll

ROOM_MODE_CHOICES = (
	('conferencing', 'Conferencing'),
	('voting', 'Voting'),
)

class Room(models.Model):
	poll = models.ForeignKey(Poll, unique=True)
	current_members = models.ManyToManyField(User, related_name="member_of", editable=False)
	opened_by = models.ForeignKey(User, related_name="opened_rooms")
	opened_at = models.DateTimeField(auto_now_add=True)
	mode = models.CharField(max_length=20, choices=ROOM_MODE_CHOICES, editable=False, default='conferencing')
	next_vote_at = models.DateTimeField(editable=False)
	
	def get_and_mark(self, user):
		messages = self.messages.exclude(read_by=user)
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread(self, user):
		return self.messages.exclude(read_by=user)
	
	def save(self, *args, **kwargs):
		if not self.id:
			now = datetime.datetime.now()
			next_vote = now + datetime.timedelta(minutes=10)
			self.next_vote_at = next_vote
		super(Room, self).save(*args, **kwargs)
	
	@models.permalink
	def get_absolute_url(self):
		return ('rooms_conference_room', [self.id])
	
	def __unicode__(self):
		return self.poll.question
	
class Message(models.Model):
	room = models.ForeignKey(Room, related_name="messages")
	author = models.ForeignKey(User, related_name="messages")
	content = models.TextField()
	read_by = models.ManyToManyField(User, blank=True, related_name="read_messages")
	created = models.DateTimeField(auto_now_add=True)
	
	def mark_for(self, user):
		self.read_by.add(user)
	
	def __unicode__(self):
		return self.content
