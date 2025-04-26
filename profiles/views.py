from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from checkout.models import Order, Payment
from checkout.forms import OrderForm
from cart.models import Cart, CartItem
from .forms import UserForm, UserProfileForm
from .models import UserProfile

@login_required
def profile(request):
    """ Display the user's profile. """
    template = 'profiles/profile.html'
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created')

    # Initialize both forms
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'Profile picture updated successfully')
            return redirect('profiles:profile')
        
        # Determine which form was submitted
        if 'update_personal' in request.POST:
            user_form = UserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Personal information updated successfully')
            else:
                messages.error(request, 'Failed to update personal information. Please check the form.')
        elif 'update_shipping' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Shipping information updated successfully')
            else:
                messages.error(request, 'Failed to update shipping information. Please check the form.')
        else:
            messages.error(request, 'Invalid form submission.')

    context = {
        'profile': profile,
        'orders': orders,
        'user_form': user_form,
        'profile_form': profile_form,
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

@login_required
def order_tracking(request, order_number):
    """ Display order tracking information. """
    template = 'profiles/order_tracking.html'
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Calculate estimated delivery if not set
    if not order.estimated_delivery and order.shipping_date:
        from datetime import timedelta
        order.estimated_delivery = order.shipping_date + timedelta(days=3)
        order.save()

    context = {
        'order': order,
    }

    return render(request, template, context)