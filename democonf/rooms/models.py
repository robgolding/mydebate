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
	"""Model to represent the "room", or debate object. Points to a Question, 
	which in turn points to the current Poll and all the choices/votes.
	Also stores the slug, which is a denormalised field for the test of the question,
	so rooms can be identified quickly.
	Rooms are always "soft-deleted" by default (i.e. is_deleted=True), which means
	they don't show up when the default manager is used.
	"""
	question = models.ForeignKey(Question, unique=True)
	opened_by = models.ForeignKey(User, related_name="opened_rooms", db_index=True)
	opened_at = models.DateTimeField(auto_now_add=True, db_index=True)
	period_length = models.IntegerField()
	next_vote_at = models.DateTimeField(editable=False)
	join_threshold = models.IntegerField()
	slug = models.CharField(max_length=200, editable=False, unique=True, db_index=True)
	is_deleted = models.BooleanField(default=False, editable=False)
	mode = models.CharField(max_length=20, default="conferencing", editable=False)
	
	# custom managers to show non-deleted, all, and only deleted objects respectively
	objects = managers.RoomManager()
	all = models.Manager()
	deleted = managers.DeletedRoomManger()
	
	@property
	def members(self):
		"""A property method to mirror the "interface" of a ManyToManyRelatedManager,
		which allows us to "add" and "remove" users from the list of current members
		in a room, whilst the backend implementation uses a relationship table (Membership)
		to store the links.
		"""
		return managers.RoomMembersManager(self)
	
	def is_active(self):
		"""Are there any members in here?"""
		return bool(self.members.all())
	
	def get_all_messages(self):
		"""Get all messages, and don't mark them read."""
		return self.messages.all()
	
	def get_all_and_mark(self, user):
		"""Get all messages, and mark them read."""
		messages = self.get_all_messages()
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread(self, user):
		"""Get only unread messages, and don't mark them read."""
		return self.messages.exclude(read_by=user)
	
	def get_unread_and_mark(self, user):
		"""Get only unread messages, and mark them read."""
		messages = self.get_unread(user)
		for message in messages:
			message.mark_for(user)
		return messages
	
	def send_system_message(self, message):
		"""Send a system message to the room."""
		m = Message(room=self, author=utils._get_system_user(), content=message)
		m.save()
		return m
	
	def _set_conferencing_mode(self):
		"""Set the room to conferencing mode. Also compares this with the room's previous
		status, and sends a system message if it has changed.
		"""
		if self.mode != "conferencing":
			self.mode = "conferencing"
			self.save()
			last_poll = self.question.get_last_poll()
			if last_poll:
				majority = last_poll.get_majority()
				if majority:
					choice = majority[0]
					votes = majority[1]
					str = "**** Vote ended (majority '%(choice)s' with %(pc)d%%) ****"
					pc = int(votes / last_poll.get_num_votes() * 100)
					message = str % {'choice': choice, 'pc': pc}
					self.send_system_message(message)
				else:
					self.send_system_message("**** Vote ended (no majority) ****")
			else:
				self.send_system_message("**** Vote ended (majority unknown) ****")
	
	def _set_voting_mode(self):
		"""Set the room to voting mode. Again, compares this with the room's previous
		status, and sends a system message if it has changed.
		"""
		if self.mode != "voting":
			self.mode = "voting"
			self.save()
			self.send_system_message("**** Vote started ****")
	
	def get_mode(self):
		"""Get the room's current mode, by comparing the current time to 
		the time of the next poll.
		"""
		now = datetime.datetime.now()
		if now < self.next_vote_at:
			self._set_conferencing_mode()
			return "conferencing"
		else:
			self._set_voting_mode()
			return "voting"
	
	def is_joinable(self):
		"""Is the room in "join" or "lock" mode. Compares the time to next vote with
		the join threshold value.
		"""
		return not self.is_active() or self.get_time_to_next_vote()/60 >= self.join_threshold
	
	def get_time_to_next_vote(self):
		"""How long is it until we go to another poll?"""
		now = datetime.datetime.now()
		if self.next_vote_at < now:
			# we've gone past it, so the next poll is _now_
			return 0
		else:
			return (self.next_vote_at - now).seconds
	
	def get_time_until_joinable(self):
		"""How long will it be until users are able to join the room?"""
		time = self.get_time_to_next_vote() - self.join_threshold
		return time if time >= 0 else 0
	
	def reset(self):
		"""Reset the room, by creating resetting the question (creates a new poll, which 
		becomes the current one) and resetting the timer to a full period length.
		"""
		self.question.reset()
		now = datetime.datetime.now()
		self.next_vote_at = now + datetime.timedelta(seconds=self.period_length*60)
		self.save()
	
	def save(self, *args, **kwargs):
		"""Overridden save() method, which sets the slug of the room and the next_vote_at
		value if we are creating a room.
		"""
		if self.question is not None:
			self.slug = slugify(self.question.text)
		if not self.id:
			now = datetime.datetime.now()
			self.next_vote_at = now + datetime.timedelta(seconds=self.period_length*60)
		super(Room, self).save(*args, **kwargs)
	
	def delete(self, delete_from_db=False, *args, **kwargs):
		"""Overridden delete() method, which soft deletes the object by default."""
		if delete_from_db:
			return super(Room, self).delete(*args, **kwargs)
		self.is_deleted = True
		super(Room, self).save(*args, **kwargs)
	
	@models.permalink
	def get_absolute_url(self):
		"""Return the absolute url to the room, using permalink decorator to reverse
		lookup the URL.
		"""
		return ('rooms_conference_room', [self.slug])
	
	def __unicode__(self):
		"""Represent the room as a unicode string."""
		return self.question.text

class Membership(models.Model):
	"""Membership model, to represent the presence of a user in a room. PK is a UUID
	as we'll have loads of these. Updated field stored the last time the user was active,
	so inactive memberships can be removed periodically.
	"""
	id = models.CharField(max_length=64, primary_key=True)
	room = models.ForeignKey(Room)
	user = models.ForeignKey(User, unique=True)
	updated = models.DateTimeField(auto_now_add=True, auto_now=True)
	
	# custom manager to allow access to the stale memberships easily
	objects = managers.MembershipManager()
	
	def save(self, *args, **kwargs):
		"""Overridden save(), to give the object a UUID primary key upon creation."""
		if not self.id:
			self.id = str(uuid4())
		super(Membership, self).save(*args, **kwargs)
	
	def touch(self):
		"""Poke the current membership, to signify the user is active."""
		self.save()
	
	def __unicode__(self):
		"""Represent the membership as a unicode string. E.g.:
			Rob Golding -> Does God Exist?
		"""
		return "%s -> %s" % (self.user, self.room)

class Message(models.Model):
	"""Simple model to represent the messages. Primary key is a UUID as there will be a
	lot of messages. Stores the room the message belongs to, and the user that posted it.
	Also stores a list of users that have read the message, which allows the system to only
	give users the messages that they haven't yet read (saves a lot of bandwidth and CPU time).
	"""
	id = models.CharField(max_length=64, primary_key=True)
	room = models.ForeignKey(Room, related_name="messages")
	author = models.ForeignKey(User, related_name="messages")
	content = models.TextField()
	read_by = models.ManyToManyField(User, blank=True, related_name="read_messages")
	created = models.DateTimeField(auto_now_add=True)
	
	def mark_for(self, user):
		"""Mark the current message as read for the given user."""
		self.read_by.add(user)
	
	def save(self, *args, **kwargs):
		"""Assign a UUID primary key upon creation."""
		if not self.id:
			self.id = str(uuid4())
		super(Message, self).save(*args, **kwargs)
	
	def __unicode__(self):
		"""Represent as a unicode string (just the message content)."""
		return self.content
