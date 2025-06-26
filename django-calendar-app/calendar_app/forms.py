from django import forms
from .models import Client, Note
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class ClientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone_number']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']


class ClientRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ClientLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
    password = forms.CharField(widget=forms.PasswordInput)