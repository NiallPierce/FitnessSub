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

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    current_cart = cart_contents(request)
    cart_items = current_cart['cart_items']
    total = current_cart['total']
    quantity = current_cart['quantity']

    if quantity <= 0:
        messages.error(request, "Your cart is empty")
        return redirect('products')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = total
            data.tax = total * 0.1  # 10% tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Create order items
            for item in cart_items:
                order_item = OrderItem()
                order_item.order = data
                order_item.product = item.product
                order_item.quantity = item.quantity
                order_item.product_price = item.product.price
                order_item.ordered = True
                order_item.save()

            # Process payment with Stripe
            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'order_number': order_number
                    }
                )

                # Create payment record
                payment = Payment.objects.create(
                    order=data,
                    payment_id=intent.id,
                    payment_method='Stripe',
                    amount_paid=total,
                    status='pending'
                )

                # Clear the cart
                cart_items.delete()

                messages.success(request, 'Your order has been placed successfully!')
                return redirect('order_complete', order_number=order_number)
            except stripe.error.CardError as e:
                messages.error(request, f'Payment failed: {e.error.message}')
                return redirect('checkout')
            except Exception as e:
                messages.error(request, 'Sorry, your payment cannot be processed at this time.')
                return redirect('checkout')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'checkout/checkout.html', context)

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