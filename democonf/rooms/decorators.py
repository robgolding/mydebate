from models import Room

def update_status(f):
	def out(request, *args, **kwargs):
		response = f(request, *args, **kwargs)
		try:
			slug = kwargs['slug']
			room = Room.objects.get(slug=slug)
			room.active = bool(room.current_members.all())
			room.save()
		except Room.DoesNotExist, KeyError:
			pass
		return response
	return out
