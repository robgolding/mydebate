import utils

class ConferenceRoomMiddleware:
	
	def process_request(self, request):
		utils.delete_stale_memberships()
