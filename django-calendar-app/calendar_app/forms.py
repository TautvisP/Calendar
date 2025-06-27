from django import forms
from .models import Client, Person, Event, EventTag, PersonRole
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

class ClientRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Vartotojo vardas')
    password = forms.CharField(widget=forms.PasswordInput, label='Slaptažodis')
    class Meta:
        model = User
        fields = ['username', 'password']

class ClientLoginForm(AuthenticationForm):
    username = forms.CharField(label='Vartotojo vardas')
    password = forms.CharField(widget=forms.PasswordInput, label='Slaptažodis')

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Senas slaptažodis',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label='Naujas slaptažodis',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label='Pakartokite naują slaptažodį',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

class PersonRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label='Vardas')
    last_name = forms.CharField(label='Pavardė')
    phone_number = forms.CharField(label='Tel. Nr.', required=False)
    email = forms.EmailField(label='El. paštas', required=False)
    notes = forms.CharField(label='Užrašai', widget=forms.Textarea, required=False)
    role = forms.ModelChoiceField(queryset=PersonRole.objects.none(), required=False, label="Rolė")

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'notes', 'role']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['role'].queryset = PersonRole.objects.filter(client=user)

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data"
    )
    person = forms.ModelChoiceField(
        queryset=Person.objects.none(), required=False, label="Pasirinkite žmogų"
    )
    manual_name = forms.CharField(required=False, label="Vardas (rankiniu būdu)")
    manual_surname = forms.CharField(required=False, label="Pavardė (rankiniu būdu)")
    tag = forms.ModelChoiceField(queryset=EventTag.objects.none(), label="Žyma")
    note = forms.CharField(widget=forms.Textarea, required=False, label="Užrašas")

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
    first_name = forms.CharField(label='Vardas')
    class Meta:
        model = User
        fields = ['first_name']

class EventTagForm(forms.ModelForm):
    name = forms.CharField(label='Pavadinimas')
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), label='Spalva')
    class Meta:
        model = EventTag
        fields = ['name', 'color']

class PersonRoleForm(forms.ModelForm):
    name = forms.CharField(label='Rolės pavadinimas')
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), label='Spalva')
    class Meta:
        model = PersonRole
        fields = ['name', 'color']