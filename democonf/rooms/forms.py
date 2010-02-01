from django import forms

from models import Room

from polling.models import Poll

class RoomForm(forms.ModelForm):
	
	question = forms.CharField()
	
	def save(self, user=None, commit=True):
		poll = Poll(question=self.cleaned_data['question'])
		poll.save()
		room = super(RoomForm, self).save(commit=False)
		room.poll = poll
		if user is not None:
			room.opened_by = user
		if commit:
			room.save()
		return room
	
	class Meta:
		model = Room
		exclude = ['opened_by', 'poll']
