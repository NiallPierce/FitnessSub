from django import forms


class CartAddProductForm(forms.Form):
    """Form for adding products to the cart."""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100px'
            }
        )
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
