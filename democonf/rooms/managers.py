import datetime

from django.db import models
from django.contrib.auth.models import User

import settings

class RoomMembersManager(models.Manager):
	
	def __init__(self, room):
		self.room = room
		self.model = models.get_model("rooms", "Membership")
	
	def add(self, user):
		Membership = self.model
		try:
			m = Membership.objects.get(room=self.room, user=user)
			m.touch()
		except Membership.DoesNotExist:
			try:
				Membership.objects.get(user=user).delete()
			except Membership.DoesNotExist:
				Membership(room=self.room, user=user).save()
	
	def remove(self, user):
		Membership = self.model
		try:
			m = Membership.objects.get(room=self.room, user=user)
			m.delete()
		except Membership.DoesNotExist:
			pass
	
	def get_query_set(self):
		return User.objects.filter(membership__room=self.room)

class MembershipManager(models.Manager):
	
	def stale(self):
		threshold = datetime.datetime.now() - datetime.timedelta(seconds=settings.STALE_USER_TIMEOUT)
		return self.get_query_set().filter(updated__lt=threshold)
