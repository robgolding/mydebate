from django import forms
from django.forms.formsets import formset_factory

class PollForm(forms.Form):
	
	question = forms.CharField(max_length=200)

class ChoiceForm(forms.Form):
	
	choice = forms.CharField(max_length=200)

ChoiceFormSet = formset_factory(ChoiceForm, extra=2)

class RoomForm(forms.Form):
	
	period_length = forms.IntegerField()
