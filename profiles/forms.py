from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import os


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'phone_number',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'postal_code',
            'newsletter_subscription',
            'profile_picture'
        )
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'newsletter_subscription': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'profile_picture': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 2MB)
            if picture.size > 2 * 1024 * 1024:
                raise forms.ValidationError(
                    'Image file too large (max 2MB)'
                )

            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(picture.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    'Unsupported file extension. '
                    'Please upload a JPG, PNG, or GIF image.'
                )

        return picture
