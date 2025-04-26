from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'})) 

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        print(f"Checking email: {email}")
        if email and User.objects.filter(email=email).exists():
            print(f"Email {email} already exists")
            self.add_error('email', "This email address is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        print(f"Clean method - email: {email}")
        if email and User.objects.filter(email=email).exists():
            print(f"Clean method - email {email} already exists")
            self.add_error('email', "This email address is already in use.")
        return cleaned_data

    def save(self, commit=True):
        print(f"Save method - is_valid: {self.is_valid()}")
        print(f"Save method - errors: {self.errors}")
        if not self.is_valid():
            raise forms.ValidationError("Form is invalid")
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user 