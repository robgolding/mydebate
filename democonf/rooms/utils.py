from django.db.models import get_model
from django.contrib.auth.models import User

SYSTEM_USERNAME = "system"

def _get_system_user():
	try:
		return User.objects.get(username=SYSTEM_USERNAME)
	except User.DoesNotExist:
		system = User(username=SYSTEM_USERNAME)
		system.set_unusable_password()
		system.save()
		return system
