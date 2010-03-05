from django.db.models import get_model
from django.contrib.auth.models import User

"""Utility methods for the 'rooms' app."""

# the default username for the system account (posts messages into rooms)
SYSTEM_USERNAME = "system"

def _get_system_user():
	"""Method to get the system user from the Django auth app. If it doesn't exist, 
	then it creates one.
	"""
	try:
		# try and get the system user and return it
		return User.objects.get(username=SYSTEM_USERNAME)
	except User.DoesNotExist:
		# if it doesn't exist already, then create a new one
		system = User(username=SYSTEM_USERNAME)
		
		# set an unusable password, so it can never be logged into
		system.set_unusable_password()
		
		#save the user, and return it
		system.save()
		return system
