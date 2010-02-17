from democonf.rooms.models import Membership

def delete_stale_memberships():
	for m in Membership.objects.stale():
		m.delete()
