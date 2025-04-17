from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from checkout.models import Order, Payment
from cart.models import Cart, CartItem
from .forms import UserForm, UserProfileForm
from .models import UserProfile

@login_required
def profile(request):
    """ Display the user's profile. """
    template = 'profiles/profile.html'
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'profile': profile,
        'orders': orders,
    }

    return render(request, template, context)

@login_required
def order_history(request, order_number):
    """ Display a past order. """
    template = 'checkout/checkout_success.html'
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)