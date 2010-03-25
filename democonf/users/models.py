## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.ForeignKey(User)
	about_me = models.TextField(blank=True)
	
	@models.permalink
	def get_absolute_url(self):
		return ('users_user_detail', (), { 'username': self.user.username })
	
	def __unicode__(self):
		return '[Profile] %s' % self.user.username
