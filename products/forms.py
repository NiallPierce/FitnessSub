from django import forms
from .models import Review, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'image',
            'stock',
            'is_featured'
        ]
        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
            'price': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'stock': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'is_featured': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
        }
