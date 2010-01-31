from django import forms

from models import Room

class RoomForm(forms.ModelForm):
	
	def save(self, user, commit=True):
		room = super(RoomForm, self).save(commit=False)
		room.opened_by = user
		if commit:
			room.save()
		return room
	
	class Meta:
		model = Room
