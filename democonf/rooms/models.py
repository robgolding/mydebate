import datetime
from uuid import uuid4
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

import managers, utils
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
	is_deleted = models.BooleanField(default=False, editable=False)
	mode = models.CharField(max_length=20, default="conferencing", editable=False)
	
	objects = managers.RoomManager()
	all = models.Manager()
	deleted = managers.DeletedRoomManger()
	
	@property
	def members(self):
		return managers.RoomMembersManager(self)
	
	def is_active(self):
		return bool(self.members.all())
	
	def get_all_messages(self):
		return self.messages.all()
	
	def get_all_and_mark(self, user):
		messages = self.get_all_messages()
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread_and_mark(self, user):
		messages = self.messages.exclude(read_by=user)
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread(self, user):
		return self.messages.exclude(read_by=user)
	
	def send_system_message(self, message):
		m = Message(room=self, author=utils._get_system_user(), content=message)
		m.save()
		return m
	
	def _set_conferencing_mode(self):
		if self.mode != "conferencing":
			self.mode = "conferencing"
			self.save()
			self.send_system_message("**** Vote ended ****")
	
	def _set_voting_mode(self):
		if self.mode != "voting":
			self.mode = "voting"
			self.save()
			self.send_system_message("**** Vote started ****")
	
	def get_mode(self):
		now = datetime.datetime.now()
		if now < self.next_vote_at:
			self._set_conferencing_mode()
			return "conferencing"
		else:
			self._set_voting_mode()
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
	
	def delete(self, delete_from_db=False, *args, **kwargs):
		if delete_from_db:
			return super(Room, self).delete(*args, **kwargs)
		self.is_deleted = True
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
