from django import forms

class DatetimeStringForm(forms.Form):
  timestamp = forms.CharField(label="Datetime object string", max_length=200)