import datetime
import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from cart.contexts import cart_contents
from .forms import OrderForm
from .models import Order, OrderItem, Payment
from cart.cart import Cart
from .forms import OrderCreateForm

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Create Stripe checkout session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Order #{order.id}',
                            },
                            'unit_amount': int(order.get_total_cost() * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/checkout/success/{order.id}/'),
                    cancel_url=request.build_absolute_uri('/checkout/cancel/'),
                    metadata={
                        'order_id': order.id
                    }
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
                return redirect('checkout:checkout')
    else:
        form = OrderCreateForm()
    
    return render(request, 'checkout/checkout.html', {
        'cart': cart,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

def payment_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order.paid = True
    order.save()
    
    # Clear the cart
    cart = Cart(request)
    cart.clear()
    
    return render(request, 'checkout/success.html', {'order': order})

def payment_cancel(request):
    return render(request, 'checkout/cancel.html')

def order_complete(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderItem.objects.filter(order=order)
        payment = Payment.objects.get(order=order)
        context = {
            'order': order,
            'order_items': order_items,
            'payment': payment,
        }
        return render(request, 'checkout/order_complete.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home') 