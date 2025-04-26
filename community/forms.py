from django import forms
from .models import SocialPost, Comment, GroupWorkout, Challenge


class SocialPostForm(forms.ModelForm):
    class Meta:
        model = SocialPost
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'image': forms.FileInput(
                attrs={'class': 'form-control'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
        }


class GroupWorkoutForm(forms.ModelForm):
    class Meta:
        model = GroupWorkout
        fields = [
            'title', 'description', 'workout_type', 'date_time',
            'duration', 'max_participants', 'location', 'meeting_link'
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'workout_type': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'date_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'duration': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'max_participants': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'meeting_link': forms.URLInput(
                attrs={'class': 'form-control'}
            ),
        }


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'start_date',
            'end_date', 'points'
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'start_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'end_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'points': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
        }
