from django import forms
from django.contrib.auth.models import User


MEAL_TYPE = (
    ('BREAKFAST', 'завтрак'),
    ('LUNCH', 'обед'),
    ('DINNER', 'ужин'),
)


class DaysForm(forms.Form):
    days = forms.ChoiceField(
        label='days',
        choices=tuple(zip(range(1, 8), (range(1, 8)))),
    )


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)