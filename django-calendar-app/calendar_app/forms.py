from django import forms
from .models import Client, Note, Person, Event, EventTag
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


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

class PersonRegistrationForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'notes']

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date"
    )
    person = forms.ModelChoiceField(
        queryset=Person.objects.none(), required=False, label="Select Person"
    )
    manual_name = forms.CharField(required=False, label="Manual Name")
    manual_surname = forms.CharField(required=False, label="Manual Surname")
    tag = forms.ModelChoiceField(queryset=EventTag.objects.none())

    class Meta:
        model = Event
        fields = ['date', 'person', 'manual_name', 'manual_surname', 'tag', 'note']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['person'].queryset = Person.objects.filter(client=user)
            self.fields['tag'].queryset = EventTag.objects.filter(client=user)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']

class EventTagForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    class Meta:
        model = EventTag
        fields = ['name', 'color']