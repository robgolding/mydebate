import datetime

from django.db import models
from django.contrib.auth.models import User

import settings

"""Custom managers for the 'rooms' app."""

class RoomManager(models.Manager):
	"""Show only non-deleted rooms (allows soft-deletion)."""
	def get_query_set(self):
		return super(RoomManager, self).get_query_set().filter(is_deleted=False, is_completed=False)

class DeletedRoomManger(models.Manager):
	"""Show only deleted rooms (extra manager to access deleted rooms)."""
	def get_query_set(self):
		return super(DeletedRoomManger, self).get_query_set().filter(is_deleted=True)

class CompletedRoomManager(models.Manager):
	"""Show only completed rooms."""
	def get_query_set(self):
		return super(CompletedRoomManager, self).get_query_set().filter(is_completed=True)

class RoomMembersManager(models.Manager):
	"""A slightly hacky approach to implementing the ManyToManyRelatedManager 'interface'.
	Allows the 'members' field to be used as a normal ManyToManyField, so we can add or remove users
	to the list of current members in a room, without noticing the implementation details
	(which is a separate joining table called Membership).
	"""
	def __init__(self, room):
		"""Initialise the manager with a copy of the room it relates to, and 
		a pointer to the membership model.
		"""
		self.room = room
		self.model = models.get_model("rooms", "Membership")
	
	def get_query_set(self):
		"""Return all users that belong to the current room, by traversing the relationship
		through Membership).
		"""
		return User.objects.filter(membership__room=self.room)
	
	def add(self, user):
		"""Add a user to the current room:
			- If they aren't already present, create a new Membership object
			- If they *are* already present, 'touch' the membership object (to signify that they are
				still active)
		"""
		Membership = self.model
		try:
			# attempt to get a membership object for the current room/user
			m = Membership.objects.get(room=self.room, user=user)
			
			#if it exists, then poke it
			m.touch()
			return True
		except Membership.DoesNotExist:
			# if not, then we'll remove the user from any other rooms, and create a new one for this room
			try:
				# try and get a membership object for the current user (in any room), and delete it
				Membership.objects.get(user=user)
				return False
			except Membership.DoesNotExist:
				# if the user wasn't in any rooms after all, it doesn't matter
				# make a new membership object and save it back
				Membership(room=self.room, user=user).save()
				return True
		return False
	
	def remove(self, user):
		"""Remove a user from the current room by deleting the membership object if it exists."""
		Membership = self.model
		try:
			# try and get the membership object, and delete it
			m = Membership.objects.get(room=self.room, user=user)
			m.delete()
		except Membership.DoesNotExist:
			# act like the ManyToManyRelatedManger, and don't raise an exception if it
			# didn't exist in the first place
			pass

class MembershipManager(models.Manager):
	"""Simple manager for the Membership model, which allows access to the 'stale' memberships quickly."""
	def stale(self):
		# use the STALE_USER_TIMEOUT value in the settings file to retrieve all membership
		# objects that haven't been updated in a time that is greater than this value
		threshold = datetime.datetime.now() - datetime.timedelta(seconds=settings.STALE_USER_TIMEOUT)
		return self.get_query_set().filter(updated__lt=threshold)
