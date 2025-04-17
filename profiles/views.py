from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from checkout.models import Order
from .forms import UserForm, UserProfileForm

@login_required
def profile(request):
    """ Display the user's profile """
    user = request.user
    profile = user.userprofile
    orders = Order.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profiles:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
    }
    return render(request, 'profiles/profile.html', context)

@login_required
def order_history(request, order_number):
    """ Display the user's order history """
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_items = order.orderitem_set.all()
        payment = order.payment_set.first()

        context = {
            'order': order,
            'order_items': order_items,
            'payment': payment,
            'from_profile': True,
        }
        return render(request, 'checkout/order_complete.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('profiles:profile')