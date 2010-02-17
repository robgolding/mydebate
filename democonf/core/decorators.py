
def remove_from_rooms(f):
	def out(request, *args, **kwargs):
		rooms = request.user.member_of.all()
		for room in rooms:
			pass
		return f(request, *args, **kwargs)
	return out
