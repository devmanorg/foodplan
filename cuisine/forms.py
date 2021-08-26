from django import forms


class DaysForm(forms.Form):
    days = forms.IntegerField(label='days')
