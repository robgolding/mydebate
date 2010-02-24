from django import forms
from django.forms.formsets import formset_factory

PERIOD_LENGTH_CHOICES = (
	(2, 2),
	(5, 5),
	(10, 10),
	(15, 15),
	(20, 20),
	(30, 30),
	(45, 45),
	(60, 60),
	(90, 90),
	(120, 120),
)

INITIAL_PERIOD_LENGTH = 30
INITIAL_JOIN_THRESHOLD = 5

class PollForm(forms.Form):
	
	question = forms.CharField(max_length=200)

class ChoiceForm(forms.Form):
	
	choice = forms.CharField(max_length=200)

ChoiceFormSet = formset_factory(ChoiceForm, extra=2)

class RoomForm(forms.Form):
	
	period_length = forms.IntegerField(
		label="Debate length (minutes):",
		widget=forms.Select(choices=PERIOD_LENGTH_CHOICES),
		initial=INITIAL_PERIOD_LENGTH
	)
	join_threshold = forms.IntegerField(
		label="Join threshold (minutes):",
		widget=forms.TextInput(),
		initial=INITIAL_JOIN_THRESHOLD,
		help_text="Prevent new members joining when there is less than this long remaining before the next poll."
	)
	
	def clean(self):
		cleaned_data = self.cleaned_data
		period_length = cleaned_data.get('period_length')
		join_threshold = cleaned_data.get('join_threshold')
		
		if join_threshold >= period_length:
			raise forms.ValidationError("Join threshold must be less than the period length.")
		
		if join_threshold < 1:
			raise forms.ValidationError("Join threshold must be at least one minute.")
		
		return cleaned_data
