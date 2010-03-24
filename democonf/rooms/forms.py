## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django import forms
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet

"""Forms for the 'rooms' app."""

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
	"""To create a poll, all we need is the question."""
	question = forms.CharField(max_length=200)

class ChoiceForm(forms.Form):
	"""For a choice, we just need to know it's name."""
	choice = forms.CharField(max_length=200)

class BaseChoiceFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			# Don't bother validating the formset unless each form is valid on its own
			return
		
		choices = []
		for i in range(0, self.total_form_count()):
			form = self.forms[i]
			choice = form.cleaned_data.get('choice', None)
			if choice:
				choices.append(choice)
		
		if len(choices) < 2:
			raise forms.ValidationError("You must create at least two choices")


# Make a FormSet from the ChoiceForm, and make the default number 2.
# Allows users to add as many choices as they like to a question.
ChoiceFormSet = formset_factory(ChoiceForm, formset=BaseChoiceFormSet, extra=2)

class RoomForm(forms.Form):
	"""More advanced tweaks for a room. User can specify the period length and the join threshold.
	Defaults are set at the top of the page.
	"""
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
		"""Validation method for the fields in this form:
			The join threshold must be strictly less than the length of a period,
			and also at least 1.
		"""
		cleaned_data = self.cleaned_data
		period_length = cleaned_data.get('period_length')
		join_threshold = cleaned_data.get('join_threshold')
		
		if join_threshold >= period_length:
			raise forms.ValidationError("Join threshold must be less than the period length.")
		
		if join_threshold < 1:
			raise forms.ValidationError("Join threshold must be at least one minute.")
		
		return cleaned_data
