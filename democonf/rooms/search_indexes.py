import datetime

from haystack import site
from haystack.indexes import *

from models import Room

class RoomIndex(RealTimeSearchIndex):
	text = CharField(document=True, use_template=True)
	
	def get_queryset(self):
		"""Used when the entire index for model is updated."""
		return Room.objects.all()

site.register(Room, RoomIndex)
