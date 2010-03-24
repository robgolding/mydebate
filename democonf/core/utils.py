## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from democonf.rooms.models import Membership

"""Utility functions for the core democonf app."""

def delete_stale_memberships():
	"""Delete all the stale memberships (kick users out of rooms if they have navigated away
	without leaving first.
	Uses the custom Membership manager, which accesses the STALE_USER_TIMEOUT value to calculate
	when a membership object should be deleted.
	"""
	for m in Membership.objects.stale():
		room = m.room
		m.delete()
		if room.is_active():
			m2 = room.membership_set.order_by('created')[0]
			room.controller = m2.user
			room.save()
