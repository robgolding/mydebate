## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

import datetime

from haystack import site
from haystack.indexes import *

from models import Room

class RoomIndex(RealTimeSearchIndex):
	text = CharField(document=True, use_template=True)
	is_completed = BooleanField()
	is_deleted = BooleanField()
	
	def get_queryset(self):
		"""Used when the entire index for model is updated."""
		return Room.objects.all()

site.register(Room, RoomIndex)
