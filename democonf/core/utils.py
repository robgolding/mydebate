from democonf.rooms.models import Membership

"""Utility functions for the core democonf app."""

def delete_stale_memberships():
	"""Delete all the stale memberships (kick users out of rooms if they have navigated away
	without leaving first.
	Uses the custom Membership manager, which accesses the STALE_USER_TIMEOUT value to calculate
	when a membership object should be deleted.
	"""
	for m in Membership.objects.stale():
		m.delete()
