## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

import utils

"""Middleware for the core democonf app."""

class ConferenceRoomMiddleware:
	"""Middleware class to perform extra processing for the conference room/debate system."""
	
	def process_request(self, request):
		"""process_request method is executed *before* the request is passed down the
		line to the view function.
		"""
		
		# delete all the stale memberships in the system at present
		# has the effect of kicking users out of rooms if they have 
		# closed their browser or navigated away from the room without
		# leaving first.
		utils.delete_stale_memberships()
