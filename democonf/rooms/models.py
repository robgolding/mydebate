import datetime
from uuid import uuid4

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

import managers

from polling.models import Poll, Question

ROOM_MODE_CHOICES = (
	('conferencing', 'Conferencing'),
	('voting', 'Voting'),
)

class Room(models.Model):
	question = models.ForeignKey(Question, unique=True)
	opened_by = models.ForeignKey(User, related_name="opened_rooms", db_index=True)
	opened_at = models.DateTimeField(auto_now_add=True, db_index=True)
	period_length = models.IntegerField()
	next_vote_at = models.DateTimeField(editable=False)
	join_threshold = models.IntegerField()
	slug = models.CharField(max_length=200, editable=False, unique=True, db_index=True)
	
	objects = models.Manager()
	
	@property
	def members(self):
		return managers.RoomMembersManager(self)
	
	def is_active(self):
		return bool(self.members.all())
	
	def get_and_mark(self, user):
		messages = self.messages.exclude(read_by=user)
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread(self, user):
		return self.messages.exclude(read_by=user)
	
	def get_mode(self):
		now = datetime.datetime.now()
		if now < self.next_vote_at:
			return "conferencing"
		else:
			return "voting"
	
	def is_joinable(self):
		return not self.is_active() or self.get_time_to_next_vote()/60 >= self.join_threshold
	
	def get_time_to_next_vote(self):
		now = datetime.datetime.now()
		if self.next_vote_at < now:
			return 0
		else:
			return (self.next_vote_at - now).seconds
	
	def get_time_until_joinable(self):
		time = self.get_time_to_next_vote() - self.join_threshold
		return time if time >= 0 else 0
	
	def reset(self):
		self.question.reset()
		now = datetime.datetime.now()
		self.next_vote_at = now + datetime.timedelta(seconds=self.period_length*60)
		self.save()
	
	def save(self, *args, **kwargs):
		if self.question is not None:
			self.slug = slugify(self.question.text)
		if not self.id:
			now = datetime.datetime.now()
			self.next_vote_at = now + datetime.timedelta(seconds=self.period_length*60)
		super(Room, self).save(*args, **kwargs)
	
	@models.permalink
	def get_absolute_url(self):
		return ('rooms_conference_room', [self.slug])
	
	def __unicode__(self):
		return self.question.text

class Membership(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	room = models.ForeignKey(Room)
	user = models.ForeignKey(User, unique=True)
	updated = models.DateTimeField(auto_now_add=True, auto_now=True)
	
	objects = managers.MembershipManager()
	
	def save(self, *args, **kwargs):
		if not self.id:
			self.id = str(uuid4())
		super(Membership, self).save(*args, **kwargs)
	
	def touch(self):
		self.save()
	
	def __unicode__(self):
		return "%s -> %s" % (self.user, self.room)

class Message(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	room = models.ForeignKey(Room, related_name="messages")
	author = models.ForeignKey(User, related_name="messages")
	content = models.TextField()
	read_by = models.ManyToManyField(User, blank=True, related_name="read_messages")
	created = models.DateTimeField(auto_now_add=True)
	
	def mark_for(self, user):
		self.read_by.add(user)
	
	def save(self, *args, **kwargs):
		if not self.id:
			self.id = str(uuid4())
		super(Message, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.content
